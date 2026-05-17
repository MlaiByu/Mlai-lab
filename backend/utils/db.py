import hashlib
import datetime
import pymysql
from contextlib import contextmanager
from config import Config

def _create_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

@contextmanager
def db_connection():
    conn = None
    try:
        conn = _create_connection()
        yield conn
    finally:
        if conn:
            conn.close()

def get_db_connection():
    return _create_connection()

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
        cursor.execute("SELECT id, username, role, score, created_at FROM users")
        result = cursor.fetchall()
        return result

def create_user(username, password, role='student'):
    with db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                      (username, hash_password(password), role, now))
        conn.commit()

def get_experiment_records(user_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, v.name, v.category
            FROM experiment_records r
            JOIN vulnerabilities v ON r.vulnerability_id = v.id
            WHERE r.user_id = %s
            ORDER BY r.vulnerability_id
        ''', (user_id,))
        result = cursor.fetchall()
        return result

def update_experiment_record(user_id, vulnerability_id, **kwargs):
    if not kwargs:
        return
    with db_connection() as conn:
        cursor = conn.cursor()
        keys = list(kwargs.keys())
        values = list(kwargs.values())
        set_clause = ", ".join("{} = %s".format(k) for k in keys)
        params = values + [user_id, vulnerability_id]
        cursor.execute('UPDATE experiment_records SET {} WHERE user_id = %s AND vulnerability_id = %s'.format(set_clause), params)
        conn.commit()

def insert_experiment_record(user_id, vulnerability_id, **kwargs):
    with db_connection() as conn:
        cursor = conn.cursor()
        columns = ['user_id', 'vulnerability_id'] + list(kwargs.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        params = [user_id, vulnerability_id] + list(kwargs.values())
        cursor.execute('INSERT INTO experiment_records ({}) VALUES ({})'.format(', '.join(columns), placeholders), params)
        conn.commit()

def get_experiment_record(user_id, vulnerability_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM experiment_records
            WHERE user_id = %s AND vulnerability_id = %s
        ''', (user_id, vulnerability_id))
        result = cursor.fetchone()
        return result if result else None

def create_experiment_session(user_id, session_id, vulnerability_id=None, docker_container_id=None, server_port=None):
    with db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if docker_container_id and server_port:
            cursor.execute('''
                INSERT INTO experiment_sessions (user_id, vulnerability_id, session_id, docker_container_id, server_port, start_time)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, vulnerability_id, session_id, docker_container_id, server_port, now))
        else:
            cursor.execute('''
                INSERT INTO experiment_sessions (user_id, vulnerability_id, session_id, start_time)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, vulnerability_id, session_id, now))
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

def get_experiment_sessions(user_id):
    with db_connection() as conn:
        cursor = conn.cursor()
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
            ORDER BY category, id
        ''')
        result = cursor.fetchall()
        return result

def get_vulnerability_by_id(vulnerability_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vulnerabilities WHERE id = %s', (vulnerability_id,))
        result = cursor.fetchone()
        return result if result else None

def add_user_score(user_id, points):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET score = score + %s WHERE id = %s', (points, user_id))
        conn.commit()

def get_user_score(user_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT score FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
        return result['score'] if result else 0


