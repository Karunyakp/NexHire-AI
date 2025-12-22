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
    
    # --- NEW TABLE FOR FULL ADMIN DATA ---
    c.execute('''CREATE TABLE IF NOT EXISTS full_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    job_role TEXT,
                    resume_text TEXT,
                    job_desc TEXT,
                    score INTEGER,
                    feedback TEXT,
                    cover_letter TEXT,
                    interview_questions TEXT,
                    market_analysis TEXT,
                    roadmap TEXT,
                    date TEXT
                )''')
    
    c.execute('CREATE TABLE IF NOT EXISTS user_preferences(username TEXT PRIMARY KEY, theme TEXT DEFAULT "light")')
    conn.commit()
    conn.close()

# --- USER AUTH ---
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

# --- DATA SAVING ---
def save_scan(username, job_role, score):
    """Saves basic stats for the User Dashboard graphs"""
    conn = get_connection()
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO history(username, job_role, score, date) VALUES (?,?,?,?)', (username, job_role, score, date))
    conn.commit()
    conn.close()

def save_full_analysis(username, job_role, resume_text, job_desc, score, feedback, cover_letter, interview_questions, market_analysis, roadmap):
    """Saves EVERYTHING for the Admin Console"""
    conn = get_connection()
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO full_analysis 
                 (username, job_role, resume_text, job_desc, score, feedback, cover_letter, interview_questions, market_analysis, roadmap, date) 
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                 (username, job_role, resume_text, job_desc, score, feedback, cover_letter, interview_questions, market_analysis, roadmap, date))
    conn.commit()
    conn.close()

# --- DATA FETCHING ---
def fetch_history(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM history WHERE username =? ORDER BY date DESC LIMIT 5', (username,))
    data = c.fetchall()
    conn.close()
    return data

def get_all_full_analysis():
    """Fetches full details for Admin"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM full_analysis ORDER BY date DESC')
    data = c.fetchall()
    conn.close()
    return data
