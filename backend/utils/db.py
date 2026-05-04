import hashlib
import datetime
import pymysql

def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='Mlai',
        password='1234',
        database='mlai_lab',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

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
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
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
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
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

def get_all_vulnerabilities():
    conn = get_db_connection()
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
    conn.close()
    return result

def get_vulnerability_by_type(vulnerability_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vulnerabilities WHERE vulnerability_type = %s', (vulnerability_type,))
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def get_vulnerabilities_by_category(category):
    conn = get_db_connection()
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
    conn.close()
    return result
