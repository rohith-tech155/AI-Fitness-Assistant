import sqlite3
import os
import hashlib
from datetime import datetime

# Path to database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'fitness.db')

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Simple SHA256 password hash helper."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Workouts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal TEXT NOT NULL,
            level TEXT NOT NULL,
            title TEXT NOT NULL,
            routine_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Progress Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# User CRUD Functions
def register_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, hashed)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {'success': True, 'user_id': user_id, 'username': username, 'email': email}
    except sqlite3.IntegrityError:
        return {'success': False, 'message': 'Username or Email already exists.'}
    finally:
        conn.close()

def login_user(username_or_email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute(
        'SELECT id, username, email FROM users WHERE (username = ? OR email = ?) AND password = ?',
        (username_or_email, username_or_email, hashed)
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return {'success': True, 'user': dict(user)}
    return {'success': False, 'message': 'Invalid credentials.'}

# Progress CRUD Functions
def add_progress(user_id, weight, date, notes=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO progress (user_id, weight, date, notes) VALUES (?, ?, ?, ?)',
        (user_id, weight, date, notes)
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return {'success': True, 'id': record_id}

def get_progress_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, weight, date, notes, created_at FROM progress WHERE user_id = ? ORDER BY date DESC',
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Workouts CRUD Functions
def save_workout(user_id, goal, level, title, routine_json):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO workouts (user_id, goal, level, title, routine_json) VALUES (?, ?, ?, ?, ?)',
        (user_id, goal, level, title, routine_json)
    )
    conn.commit()
    workout_id = cursor.lastrowid
    conn.close()
    return {'success': True, 'id': workout_id}

def get_user_workouts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, goal, level, title, routine_json, created_at FROM workouts WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Chat History Functions
def save_chat_message(user_id, sender, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)',
        (user_id, sender, message)
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id, limit=20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT sender, message, timestamp FROM chat_history WHERE user_id = ? ORDER BY id ASC LIMIT ?',
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
