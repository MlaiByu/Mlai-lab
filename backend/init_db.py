import hashlib
import datetime
import pymysql
import traceback
from config import Config

def create_database():
    conn = None
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(Config.DB_NAME))
        print("✓ 数据库创建成功或已存在")
    except Exception as e:
        print(f"✗ 创建数据库失败: {e}")
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

def init_db():
    conn = None
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        print("\n=== 开始初始化数据库表结构 ===")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'student',
                score INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                last_login DATETIME
            )
        ''')
        print("✓ users 表")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                flag VARCHAR(255) NOT NULL,
                category VARCHAR(50) NOT NULL DEFAULT 'web',
                difficulty VARCHAR(20) NOT NULL DEFAULT 'easy'
            )
        ''')
        print("✓ vulnerabilities 表")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_records (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER NOT NULL,
                vulnerability_id INTEGER NOT NULL,
                attempt_count INTEGER NOT NULL DEFAULT 0,
                success INTEGER NOT NULL DEFAULT 0,
                last_attempt DATETIME,
                first_success DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id),
                UNIQUE KEY user_vuln_unique (user_id, vulnerability_id)
            )
        ''')
        print("✓ experiment_records 表")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_sessions (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                session_id VARCHAR(255) NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                vulnerability_id INTEGER,
                docker_container_id VARCHAR(100),
                server_port INTEGER,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                success INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id)
            )
        ''')
        print("✓ experiment_sessions 表")

        print("\n=== 检查并添加缺失字段 ===")
        try:
            cursor.execute('SELECT score FROM users LIMIT 1')
            print("✓ score 字段已存在")
        except Exception:
            cursor.execute('ALTER TABLE users ADD COLUMN score INTEGER NOT NULL DEFAULT 0 AFTER role')
            print("✓ 添加 score 字段成功")

        try:
            cursor.execute('SELECT vulnerability_id FROM experiment_sessions LIMIT 1')
            print("✓ vulnerability_id 字段已存在")
        except Exception:
            cursor.execute('ALTER TABLE experiment_sessions ADD COLUMN vulnerability_id INTEGER AFTER user_id')
            print("✓ 添加 vulnerability_id 字段成功")
            cursor.execute('ALTER TABLE experiment_sessions ADD FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities(id)')
            print("✓ 添加外键约束成功")

        try:
            cursor.execute('SELECT difficulty FROM vulnerabilities LIMIT 1')
            print("✓ difficulty 字段已存在")
        except Exception:
            cursor.execute('ALTER TABLE vulnerabilities ADD COLUMN difficulty VARCHAR(20) NOT NULL DEFAULT "easy" AFTER category')
            print("✓ 添加 difficulty 字段成功")

        print("\n=== 创建索引 ===")
        indexes = [
            ("idx_users_username", "users", "username"),
            ("idx_users_role", "users", "role"),
            ("idx_exp_records_user", "experiment_records", "user_id"),
            ("idx_exp_records_vuln", "experiment_records", "vulnerability_id"),
            ("idx_exp_sessions_session", "experiment_sessions", "session_id"),
            ("idx_exp_sessions_user", "experiment_sessions", "user_id"),
            ("idx_exp_sessions_vuln", "experiment_sessions", "vulnerability_id"),
            ("idx_vulnerabilities_category", "vulnerabilities", "category"),
            ("idx_vulnerabilities_difficulty", "vulnerabilities", "difficulty")
        ]

        for idx_name, table, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})")
                print(f"✓ 索引 {idx_name}")
            except Exception as e:
                print(f"✓ 索引 {idx_name} 已存在")

        print("\n=== 初始化默认数据 ===")
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        if user_count == 0:
            admin_pass = hashlib.sha256('password'.encode()).hexdigest()
            teacher_pass = hashlib.sha256('teacherpass'.encode()).hexdigest()
            student_pass = hashlib.sha256('123456'.encode()).hexdigest()

            cursor.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                ('admin', admin_pass, 'admin', now)
            )
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                ('teacher1', teacher_pass, 'teacher', now)
            )
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                ('student1', student_pass, 'student', now)
            )
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)",
                ('student2', student_pass, 'student', now)
            )
            print("✓ 创建默认用户:")
            print("  - admin/password (管理员)")
            print("  - teacher1/teacherpass (教师)")
            print("  - student1/123456 (学生)")
            print("  - student2/123456 (学生)")
        else:
            print(f"✓ 用户表已有 {user_count} 条记录")

        cursor.execute("SELECT COUNT(*) as count FROM vulnerabilities")
        vuln_count = cursor.fetchone()['count']
        if vuln_count == 0:
            vulnerabilities_data = [
                ('SQL注入-入门', 'Mlai{sqli_easy_2026_get_flag}', 'sqli', 'easy'),
                ('SQL注入-中级', 'Mlai{sqli_medium_bypass_comment}', 'sqli', 'medium'),
                ('SQL注入-高级', 'Mlai{sqli_hard_double_write_bypass}', 'sqli', 'hard'),
                ('反射型XSS', 'Mlai{xss_reflected_flag}', 'xss', 'easy'),
                ('存储型XSS', 'Mlai{xss_stored_flag}', 'xss', 'medium'),
                ('DOM型XSS', 'Mlai{xss_dom_flag}', 'xss', 'easy'),
                ('PHP反序列化', 'Mlai{php_unserialize_flag}', 'deserialization', 'hard'),
                ('文件上传', 'Mlai{file_upload_flag}', 'upload', 'medium'),
                ('CSRF-Easy', 'Mlai{CSRF-Easy-Success}', 'csrf', 'easy'),
                ('CSRF-Hard', 'Mlai{CSRF-Hard-Success}', 'csrf', 'medium'),
                ('Python反序列化', 'Mlai{Python-Deserialization-Success}', 'deserialization', 'hard')
            ]

            for vuln in vulnerabilities_data:
                cursor.execute('''
                    INSERT INTO vulnerabilities (name, flag, category, difficulty)
                    VALUES (%s, %s, %s, %s)
                ''', vuln)
            print("✓ 创建默认漏洞数据（11个漏洞）")
        else:
            print(f"✓ 漏洞表已有 {vuln_count} 条记录")

        conn.commit()
        print("\n=== 数据库初始化完成 ===")

    except Exception as e:
        print(f"\n✗ 数据库初始化失败: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=========================================")
    print("  Mlai-Lab 数据库初始化")
    print("=========================================")
    create_database()
    init_db()