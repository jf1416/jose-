import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_PATH = 'crm.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

@contextmanager
def connect():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with connect() as conn:
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS users (
                   id TEXT PRIMARY KEY,
                   name TEXT NOT NULL,
                   email TEXT NOT NULL,
                   phone TEXT,
                   status TEXT,
                   created_at TEXT,
                   last_activity TEXT
               )'''
        )
        c.execute(
            '''CREATE TABLE IF NOT EXISTS comments (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id TEXT,
                   text TEXT,
                   timestamp TEXT,
                   author TEXT,
                   FOREIGN KEY(user_id) REFERENCES users(id)
               )'''
        )
        c.execute('SELECT COUNT(*) FROM users')
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)',
                      ('USR001', 'John Doe', 'john.doe@email.com', '+1-555-0123',
                       'active', '2024-01-15 09:30:00', '2024-01-20 14:22:00'))
            c.execute('INSERT INTO comments (user_id,text,timestamp,author) VALUES (?,?,?,?)',
                      ('USR001', 'Initial contact made', '2024-01-15 09:35:00', 'Admin'))
            c.execute('INSERT INTO comments (user_id,text,timestamp,author) VALUES (?,?,?,?)',
                      ('USR001', 'Follow-up scheduled', '2024-01-18 11:00:00', 'Sales Team'))
            c.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)',
                      ('USR002', 'Jane Smith', 'jane.smith@email.com', '+1-555-0124',
                       'pending', '2024-01-18 16:45:00', '2024-01-19 10:15:00'))
            c.execute('INSERT INTO comments (user_id,text,timestamp,author) VALUES (?,?,?,?)',
                      ('USR002', 'Awaiting documentation', '2024-01-18 16:50:00', 'Support'))
        conn.commit()

def get_all_users():
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, email, phone, status, created_at, last_activity FROM users')
        users = []
        for row in c.fetchall():
            uid = row[0]
            c.execute('SELECT id, text, timestamp, author FROM comments WHERE user_id=? ORDER BY timestamp', (uid,))
            comments = [
                {"id": str(cid), "text": text, "timestamp": ts, "author": author}
                for cid, text, ts, author in c.fetchall()
            ]
            users.append({
                'id': uid,
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'status': row[4],
                'created_at': row[5],
                'last_activity': row[6],
                'comments': comments
            })
        return users

def find_user_by_id(uid):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, email, phone, status, created_at, last_activity FROM users WHERE id=?', (uid,))
        row = c.fetchone()
        if not row:
            return None
        c.execute('SELECT id, text, timestamp, author FROM comments WHERE user_id=? ORDER BY timestamp', (uid,))
        comments = [
            {"id": str(cid), "text": text, "timestamp": ts, "author": author}
            for cid, text, ts, author in c.fetchall()
        ]
        return {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'status': row[4],
            'created_at': row[5],
            'last_activity': row[6],
            'comments': comments
        }

def add_user(name, email, phone):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users')
        new_id = f'USR{c.fetchone()[0] + 1:03d}'
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)',
                  (new_id, name, email, phone, 'pending', now, now))
        c.execute('INSERT INTO comments (user_id,text,timestamp,author) VALUES (?,?,?,?)',
                  (new_id, 'User registered in system', now, 'System'))
        conn.commit()
        return new_id

def add_comment(uid, text, author='Current User'):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with connect() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO comments (user_id,text,timestamp,author) VALUES (?,?,?,?)',
                  (uid, text, now, author))
        c.execute('UPDATE users SET last_activity=? WHERE id=?', (now, uid))
        conn.commit()
        return now

if __name__ == '__main__':
    init_db()
    print('Tables created successfully.')
