import hashlib
import datetime
import pymysql

def create_database():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='rootpass',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS mlai_lab")
        print("Database created or already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
    
    conn.close()

def init_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='rootpass',
        database='mlai_lab',
        cursorclass=pymysql.cursors.DictCursor
    )
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
            session_id VARCHAR(255) NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            vulnerability_type VARCHAR(50) NOT NULL,
            start_time VARCHAR(50) NOT NULL,
            end_time VARCHAR(50),
            success INTEGER NOT NULL DEFAULT 0,
            attempt_count INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    try:
        cursor.execute("CREATE INDEX idx_users_username ON users(username)")
    except:
        pass
    try:
        cursor.execute("CREATE INDEX idx_exp_records_user ON experiment_records(user_id)")
    except:
        pass
    try:
        cursor.execute("CREATE INDEX idx_exp_records_type ON experiment_records(vulnerability_type)")
    except:
        pass
    try:
        cursor.execute("CREATE INDEX idx_exp_sessions_session ON experiment_sessions(session_id)")
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
        print("Created default users: admin/password, user/userpass")
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

if __name__ == "__main__":
    create_database()
    init_db()