import sqlite3
import hashlib
import datetime

def get_connection():
    return sqlite3.connect('nexhire.db', check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT, is_admin INTEGER DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, job_role TEXT, score INTEGER, date TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS detailed_feedback(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, job_role TEXT, feedback TEXT, resume_skills TEXT, job_skills TEXT, date TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS user_preferences(username TEXT PRIMARY KEY, theme TEXT DEFAULT "light")')
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

def fetch_all_history(username, limit=100):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM history WHERE username =? ORDER BY date DESC LIMIT ?', (username, limit))
    data = c.fetchall()
    conn.close()
    return data

def save_detailed_feedback(username, job_role, feedback, resume_skills, job_skills):
    conn = get_connection()
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    skills_str = ",".join(resume_skills)
    job_skills_str = ",".join(job_skills)
    c.execute('INSERT INTO detailed_feedback(username, job_role, feedback, resume_skills, job_skills, date) VALUES (?,?,?,?,?,?)',
              (username, job_role, feedback, skills_str, job_skills_str, date))
    conn.commit()
    conn.close()

def get_all_scans():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM history ORDER BY date DESC')
    data = c.fetchall()
    conn.close()
    return data

def get_user_theme(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT theme FROM user_preferences WHERE username =?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "light"

def set_user_theme(username, theme):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT OR REPLACE INTO user_preferences(username, theme) VALUES (?,?)', (username, theme))
        conn.commit()
    except:
        pass
    conn.close()

def set_admin(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET is_admin=1 WHERE username=?', (username,))
    conn.commit()
    conn.close()

def is_admin(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT is_admin FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0