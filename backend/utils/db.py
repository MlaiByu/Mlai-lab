import hashlib
import datetime
import pymysql
from contextlib import contextmanager
from config import Config

@contextmanager
def db_connection():
    conn = None
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        yield conn
    finally:
        if conn:
            conn.close()

def get_db_connection():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_username(username):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result if result else None

def get_user_by_id(user_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        return result if result else None

def get_all_users():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, created_at FROM users")
        result = cursor.fetchall()
        return result

def create_user(username, password, role='student'):
    with db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                      (username, hash_password(password), role, now))
        conn.commit()

def get_experiment_records(user_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT vulnerability_type, attempt_count, success_count
            FROM experiment_records
            WHERE user_id = %s
            ORDER BY vulnerability_type
        ''', (user_id,))
        result = cursor.fetchall()
        return result

def update_experiment_record(user_id, vulnerability_type, **kwargs):
    if not kwargs:
        return
    with db_connection() as conn:
        cursor = conn.cursor()
        keys = list(kwargs.keys())
        values = list(kwargs.values())
        set_clause = ", ".join("{} = %s".format(k) for k in keys)
        params = values + [user_id, vulnerability_type]
        cursor.execute('UPDATE experiment_records SET {} WHERE user_id = %s AND vulnerability_type = %s'.format(set_clause), params)
        conn.commit()

def insert_experiment_record(user_id, vulnerability_type, **kwargs):
    with db_connection() as conn:
        cursor = conn.cursor()
        columns = ['user_id', 'vulnerability_type'] + list(kwargs.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        params = [user_id, vulnerability_type] + list(kwargs.values())
        cursor.execute('INSERT INTO experiment_records ({}) VALUES ({})'.format(', '.join(columns), placeholders), params)
        conn.commit()

def get_experiment_record(user_id, vulnerability_type):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM experiment_records
            WHERE user_id = %s AND vulnerability_type = %s
        ''', (user_id, vulnerability_type))
        result = cursor.fetchone()
        return result if result else None

def create_experiment_session(user_id, vulnerability_type, session_id, container_id=None, port=None):
    with db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if container_id and port:
            cursor.execute('''
                INSERT INTO experiment_sessions (user_id, vulnerability_type, session_id, start_time, container_id, port)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, vulnerability_type, session_id, now, container_id, port))
        else:
            cursor.execute('''
                INSERT INTO experiment_sessions (user_id, vulnerability_type, session_id, start_time)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, vulnerability_type, session_id, now))
        conn.commit()

def update_experiment_session(session_id, **kwargs):
    if not kwargs:
        return
    with db_connection() as conn:
        cursor = conn.cursor()
        keys = list(kwargs.keys())
        values = list(kwargs.values())
        set_clause = ", ".join("{} = %s".format(k) for k in keys)
        params = values + [session_id]
        cursor.execute('UPDATE experiment_sessions SET {} WHERE session_id = %s'.format(set_clause), params)
        conn.commit()

def delete_experiment_session(session_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM experiment_sessions WHERE session_id = %s', (session_id,))
        conn.commit()

def get_experiment_sessions(user_id, vulnerability_type=None):
    with db_connection() as conn:
        cursor = conn.cursor()
        if vulnerability_type:
            cursor.execute('''
                SELECT * FROM experiment_sessions
                WHERE user_id = %s AND vulnerability_type = %s
                ORDER BY start_time DESC
            ''', (user_id, vulnerability_type))
        else:
            cursor.execute('''
                SELECT * FROM experiment_sessions
                WHERE user_id = %s
                ORDER BY start_time DESC
            ''', (user_id,))
        result = cursor.fetchall()
        return result

def get_all_vulnerabilities():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM vulnerabilities
            ORDER BY CASE difficulty
                WHEN 'easy' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'hard' THEN 3
                ELSE 4
            END, vulnerability_type
        ''')
        result = cursor.fetchall()
        return result

def get_vulnerability_by_type(vulnerability_type):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vulnerabilities WHERE vulnerability_type = %s', (vulnerability_type,))
        result = cursor.fetchone()
        return result if result else None

def get_vulnerabilities_by_category(category):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM vulnerabilities
            WHERE category = %s
            ORDER BY CASE difficulty
                WHEN 'easy' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'hard' THEN 3
                ELSE 4
            END, vulnerability_type
        ''', (category,))
        result = cursor.fetchall()
        return result