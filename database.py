import sqlite3
import datetime
import hashlib
import json
import os

DB_NAME = 'nexhire.db'

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    # Create tables if they don't exist
    # explicitly defining schema to avoid mismatches
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs
                 (timestamp TEXT, username TEXT, mode TEXT, action TEXT, score INTEGER, details TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Check if user exists first to avoid Primary Key errors
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return False
            
        # Use explicit column names to prevent OperationalError if schema drifts
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
        data = c.fetchall()
        return len(data) > 0
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def save_scan(username, mode, action, score, details=None):
    conn = get_connection()
    c = conn.cursor()
    try:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = username if username else "Guest"
        
        # Ensure details are stored as a string (JSON)
        if isinstance(details, (dict, list)):
            details_str = json.dumps(details)
        else:
            details_str = str(details) if details else ""
            
        c.execute("INSERT INTO activity_logs (timestamp, username, mode, action, score, details) VALUES (?, ?, ?, ?, ?, ?)", 
                  (date, user, mode, action, score, details_str))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Save scan error: {e}")
    finally:
        conn.close()

def get_all_full_analysis():
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC")
        data = c.fetchall()
        return data
    except sqlite3.Error:
        return []
    finally:
        conn.close()

def fetch_user_history(username):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM activity_logs WHERE username = ? ORDER BY timestamp DESC", (username,))
        data = c.fetchall()
        return data
    except sqlite3.Error:
        return []
    finally:
        conn.close()
