import sqlite3
import datetime
import hashlib
import json

def create_tables():
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    # Updated schema: Added 'details' column to store full analysis data
    # Renamed table to 'activity_logs' to ensure fresh schema creation
    c.execute('''CREATE TABLE IF NOT EXISTS activity_logs
                 (timestamp TEXT, username TEXT, mode TEXT, action TEXT, score INTEGER, details TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(username, password):
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hash_password(password)))
    data = c.fetchall()
    conn.close()
    return len(data) > 0

def save_scan(username, mode, action, score, details=None):
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = username if username else "Guest"
    
    # Ensure details are stored as a string (JSON)
    if isinstance(details, (dict, list)):
        details_str = json.dumps(details)
    else:
        details_str = str(details) if details else ""
        
    c.execute("INSERT INTO activity_logs VALUES (?, ?, ?, ?, ?, ?)", (date, user, mode, action, score, details_str))
    conn.commit()
    conn.close()

def get_all_full_analysis():
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    c.execute("SELECT * FROM activity_logs ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    return data

def fetch_user_history(username):
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    c.execute("SELECT * FROM activity_logs WHERE username = ? ORDER BY timestamp DESC", (username,))
    data = c.fetchall()
    conn.close()
    return data
