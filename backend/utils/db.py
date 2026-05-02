import hashlib
import datetime
import pymysql

def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='rootpass',
        database='mlai_lab',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'student',
            created_at VARCHAR(50) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiment_records (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            user_id INTEGER NOT NULL,
            vulnerability_type VARCHAR(50) NOT NULL,
            attempt_count INTEGER NOT NULL DEFAULT 0,
            success_count INTEGER NOT NULL DEFAULT 0,
            last_attempt VARCHAR(50),
            first_success VARCHAR(50),
            total_time DECIMAL(10,2) NOT NULL DEFAULT 0,
            start_time VARCHAR(50),
            is_expired INTEGER NOT NULL DEFAULT 0,
            remaining_time INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiment_sessions (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            user_id INTEGER NOT NULL,
            vulnerability_type VARCHAR(50) NOT NULL,
            session_id VARCHAR(36) NOT NULL UNIQUE,
            start_time VARCHAR(50) NOT NULL,
            end_time VARCHAR(50),
            success INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    for index_sql in [
        "CREATE INDEX idx_users_username ON users(username)",
        "CREATE INDEX idx_exp_records_user ON experiment_records(user_id)",
        "CREATE INDEX idx_exp_records_type ON experiment_records(vulnerability_type)"
    ]:
        try:
            cursor.execute(index_sql)
        except:
            pass

    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    if result['count'] == 0:
        admin_pass = hashlib.sha256('password'.encode()).hexdigest()
        user_pass = hashlib.sha256('userpass'.encode()).hexdigest()
        now = datetime.datetime.now().isoformat()
        cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                      ('admin', admin_pass, 'teacher', now))
        cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                      ('user', user_pass, 'student', now))

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users")
    result = cursor.fetchall()
    conn.close()
    return result

def create_user(username, password, role='student'):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                  (username, hash_password(password), role, now))
    conn.commit()
    conn.close()

def get_experiment_records(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT vulnerability_type, attempt_count, success_count, last_attempt, first_success,
               total_time, start_time, is_expired, remaining_time
        FROM experiment_records
        WHERE user_id = %s
        ORDER BY vulnerability_type
    ''', (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def update_experiment_record(user_id, vulnerability_type, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join("{} = %s".format(k) for k in kwargs.keys())
    params = list(kwargs.values()) + [user_id, vulnerability_type]
    cursor.execute('UPDATE experiment_records SET {} WHERE user_id = %s AND vulnerability_type = %s'.format(set_clause), params)
    conn.commit()
    conn.close()

def insert_experiment_record(user_id, vulnerability_type, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = ['user_id', 'vulnerability_type'] + list(kwargs.keys())
    placeholders = ", ".join(["%s"] * len(columns))
    params = [user_id, vulnerability_type] + list(kwargs.values())
    cursor.execute('INSERT INTO experiment_records ({}) VALUES ({})'.format(', '.join(columns), placeholders), params)
    conn.commit()
    conn.close()

def get_experiment_record(user_id, vulnerability_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM experiment_records
        WHERE user_id = %s AND vulnerability_type = %s
    ''', (user_id, vulnerability_type))
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def create_experiment_session(user_id, vulnerability_type, session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO experiment_sessions (user_id, vulnerability_type, session_id, start_time)
        VALUES (%s, %s, %s, %s)
    ''', (user_id, vulnerability_type, session_id, now))
    conn.commit()
    conn.close()

def update_experiment_session(session_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join("{} = %s".format(k) for k in kwargs.keys())
    params = list(kwargs.values()) + [session_id]
    cursor.execute('UPDATE experiment_sessions SET {} WHERE session_id = %s'.format(set_clause), params)
    conn.commit()
    conn.close()

def delete_experiment_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM experiment_sessions WHERE session_id = %s', (session_id,))
    conn.commit()
    conn.close()

def get_experiment_sessions(user_id, vulnerability_type=None):
    conn = get_db_connection()
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
    conn.close()
    return result
