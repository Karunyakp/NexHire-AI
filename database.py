import sqlite3
import datetime

def create_tables():
    """Creates the necessary database tables if they don't exist."""
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    # Simplified table: We track Time, Mode (Candidate/Recruiter), Action, and Score
    c.execute('''CREATE TABLE IF NOT EXISTS scans
                 (timestamp TEXT, mode TEXT, action TEXT, score INTEGER)''')
    conn.commit()
    conn.close()

def save_scan(mode, action, score):
    """Silently saves a scan record without needing a username."""
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Insert the data
    c.execute("INSERT INTO scans VALUES (?, ?, ?, ?)", (date, mode, action, score))
    conn.commit()
    conn.close()

def get_all_full_analysis():
    """Fetches all records for the Hidden Admin Console."""
    conn = sqlite3.connect('nexhire.db')
    c = conn.cursor()
    c.execute("SELECT * FROM scans ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    # Returns a list of tuples: [(Time, Mode, Action, Score), ...]
    return data
