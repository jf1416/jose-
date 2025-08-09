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
        c.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                loan_number TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                id_number TEXT NOT NULL,
                address TEXT,
                locality TEXT,
                note TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loan_number TEXT,
                text TEXT,
                timestamp TEXT,
                FOREIGN KEY(loan_number) REFERENCES clients(loan_number)
            )
        ''')
        conn.commit()

def add_client(loan_number, name, id_number, address, locality, note):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with connect() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO clients VALUES (?,?,?,?,?,?,?,?)',
                  (loan_number, name, id_number, address, locality, note, now, now))
        conn.commit()

def update_client(loan_number, name, id_number, address, locality, note):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE clients
            SET name=?, id_number=?, address=?, locality=?, note=?, updated_at=?
            WHERE loan_number=?
        ''', (name, id_number, address, locality, note, now, loan_number))
        conn.commit()

def delete_client(loan_number):
    with connect() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM comments WHERE loan_number=?', (loan_number,))
        c.execute('DELETE FROM clients WHERE loan_number=?', (loan_number,))
        conn.commit()

def get_all_clients():
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT loan_number, name, id_number, address, locality, note, created_at, updated_at
            FROM clients ORDER BY created_at DESC
        ''')
        return [
            {
                'loan_number': row[0],
                'name': row[1],
                'id_number': row[2],
                'address': row[3],
                'locality': row[4],
                'note': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            }
            for row in c.fetchall()
        ]

def search_clients(term):
    like = f"%{term}%"
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT loan_number, name, id_number, address, locality, note, created_at, updated_at
            FROM clients
            WHERE loan_number LIKE ? OR id_number LIKE ? OR name LIKE ?
            ORDER BY created_at DESC
        ''', (like, like, like))
        return [
            {
                'loan_number': row[0],
                'name': row[1],
                'id_number': row[2],
                'address': row[3],
                'locality': row[4],
                'note': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            }
            for row in c.fetchall()
        ]

def get_client(loan_number):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT loan_number, name, id_number, address, locality, note, created_at, updated_at
            FROM clients WHERE loan_number=?
        ''', (loan_number,))
        row = c.fetchone()
        if not row:
            return None
        return {
            'loan_number': row[0],
            'name': row[1],
            'id_number': row[2],
            'address': row[3],
            'locality': row[4],
            'note': row[5],
            'created_at': row[6],
            'updated_at': row[7]
        }

def get_comments(loan_number):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT id, text, timestamp FROM comments WHERE loan_number=? ORDER BY timestamp', (loan_number,))
        return [
            {'id': row[0], 'text': row[1], 'timestamp': row[2]}
            for row in c.fetchall()
        ]

def add_comment(loan_number, text):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with connect() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO comments (loan_number, text, timestamp) VALUES (?,?,?)',
                  (loan_number, text, now))
        conn.commit()
        return now

if __name__ == '__main__':
    init_db()
    print('Tables created successfully.')
