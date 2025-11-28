import sqlite3
import hashlib
import datetime

def get_connection():
    return sqlite3.connect('nexhire.db', check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(username TEXT, job_role TEXT, score INTEGER, date TEXT)')
    conn.commit()
    conn.close()
def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    hashed_pw = hashlib.sha256(str.encode(password)).hexdigest()
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, hashed_pw))
    data = c.fetchall()
    conn.close()
    return data

def add_user(username, password):
    try:
        conn = get_connection()
        c = conn.cursor()
        hashed_pw = hashlib.sha256(str.encode(password)).hexdigest()
        c.execute('INSERT INTO users(username, password) VALUES (?,?)', (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except:
        return False 

def save_scan(username, job_role, score):
    conn = get_connection()
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO history(username, job_role, score, date) VALUES (?,?,?,?)', (username, job_role, score, date))
    conn.commit()
    conn.close()

def fetch_history(username):
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM history WHERE username =? ORDER BY date DESC LIMIT 5', (username,))
    data = c.fetchall()
    conn.close()
    return data