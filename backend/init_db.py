import hashlib
import datetime
import pymysql
from config import Config

def create_database():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(Config.DB_NAME))
        print("Database created or already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
    
    conn.close()

def init_db():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
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
            end_time VARCHAR(50),
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            vulnerability_type VARCHAR(50) NOT NULL UNIQUE,
            flag VARCHAR(255) NOT NULL,
            solution TEXT,
            description TEXT,
            difficulty VARCHAR(20) NOT NULL DEFAULT 'easy',
            category VARCHAR(50) NOT NULL DEFAULT 'web',
            created_at VARCHAR(50) NOT NULL
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
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)", 
                      ('admin', admin_pass, 'teacher', now))
        cursor.execute("INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, %s)", 
                      ('user', user_pass, 'student', now))
        print("Created default users: admin/password, user/userpass")

    cursor.execute("SELECT COUNT(*) as count FROM vulnerabilities")
    vuln_result = cursor.fetchone()
    if vuln_result['count'] == 0:
        vulnerabilities_data = [
            ('SQL注入-入门', 'Mlai{sqli_easy_2026_get_flag}', '1. 这是一个简单的数字型SQL注入，无任何过滤\n2. 输入1\'测试，会发现SQL语法错误\n3. 使用UNION SELECT查询获取数据：1\' UNION SELECT 1,2,3,4,5,6,7,8,9,10--\n4. 查询flag表获取flag：1\' UNION SELECT 1,2,3,4,5,6,7,8,9,flag FROM flag--', '简单的数字型SQL注入漏洞，无任何过滤措施', 'easy', 'sqli'),
            ('SQL注入-中级', 'Mlai{sqli_medium_bypass_comment}', '1. 这是一个字符型SQL注入，注释符被过滤\n2. 输入1\'测试，发现报错\n3. 由于注释符被过滤，需要闭合引号来绕过\n4. 可以使用payload：1\' union select 1,2,3,4,5,6,7,8,9,10 or \'1\'=\'1\n5. 查询flag：1\' union select 1,2,3,4,5,6,7,8,9,flag from flag or \'1\'=\'1', '字符型SQL注入，过滤了注释符', 'medium', 'sqli'),
            ('SQL注入-高级', 'Mlai{sqli_hard_double_write_bypass}', '1. 这是一个严格的SQL注入，过滤了多个关键字\n2. 常见的关键字如select、union等被过滤\n3. 可以使用双写绕过：selselectect、ununionion\n4. 双写绕过示例：1\' ununionion selselectect 1,2,3,4,5,6,7,8,9,10--\n5. 查询flag：1\' ununionion selselectect 1,2,3,4,5,6,7,8,9,flag frfromom flag--', '高级SQL注入，过滤多个关键字，需要双写绕过', 'hard', 'sqli'),
            ('反射型XSS', 'Mlai{xss_reflected_flag}', '1. 这是一个简单的反射型XSS漏洞\n2. URL参数直接输出到页面中，没有过滤\n3. 测试：输入 <script>alert(1)</script>\n4. 尝试获取cookie：<script>alert(document.cookie)</script>', '反射型XSS漏洞，URL参数未过滤', 'easy', 'xss'),
            ('存储型XSS', 'Mlai{xss_stored_flag}', '1. 这是一个存储型XSS漏洞\n2. 用户输入会被存储到服务器\n3. 在输入框中输入恶意脚本并提交\n4. 刷新页面后，脚本会自动执行', '存储型XSS漏洞，用户输入存储后执行', 'medium', 'xss'),
            ('DOM型XSS', 'Mlai{xss_dom_flag}', '1. 这是一个DOM型XSS漏洞\n2. 漏洞存在于前端JavaScript代码中\n3. 查看页面源码，找到处理用户输入的JavaScript\n4. 通常是通过location.hash或URL参数直接操作DOM', 'DOM型XSS漏洞，前端JavaScript处理不当', 'medium', 'xss'),
            ('PHP反序列化', 'Mlai{php_unserialize_flag}', '1. 这是一个PHP反序列化漏洞\n2. 程序会反序列化用户输入的数据\n3. 首先需要找到目标类的定义\n4. 构造恶意的序列化字符串\n5. 触发__wakeup或__destruct等魔术方法', 'PHP反序列化漏洞', 'hard', 'deserialization'),
            ('Python反序列化', 'Mlai{python_pickle_flag}', '1. 这是一个Python pickle反序列化漏洞\n2. pickle模块是不安全的，不要反序列化不信任的数据\n3. 构造恶意的pickle数据\n4. 可以使用__reduce__方法执行任意命令', 'Python pickle反序列化漏洞', 'hard', 'deserialization'),
            ('文件上传', 'Mlai{file_upload_flag}', '1. 这是一个文件上传漏洞\n2. 尝试上传.php文件\n3. 如果有MIME类型检查，可以通过修改Content-Type绕过\n4. 如果有扩展名检查，可以尝试.php5、.php3或双重扩展名', '文件上传漏洞', 'medium', 'upload'),
            ('CSRF-Easy', 'Mlai{CSRF-Easy-Success}', '1. 这是一个无任何CSRF防护的漏洞\n2. 构造一个恶意页面，包含自动提交的表单\n3. 表单的action指向目标URL\n4. 输入框中填入要修改的数据（密码改成hacked!）\n5. 诱骗已登录的用户访问恶意页面\n6. 访问?get_flag=1获取flag', 'CSRF跨站请求伪造漏洞，无任何防护', 'easy', 'csrf'),
            ('CSRF-Hard', 'Mlai{CSRF-Hard-Success}', '1. 这是一个有Referer检查的CSRF漏洞\n2. Referer检查使用了strpos($referer, $host) !== false\n3. 可以通过构造URL子域名或路径来绕过\n4. 如：构造http://target-server.attacker.com 或者 http://attacker.com/target-server.com\n5. 完成任务：转账999元给attacker + 修改密码为hacked! + 访问?get_flag=1', 'CSRF跨站请求伪造漏洞，有Referer检查但可绕过', 'hard', 'csrf')
        ]
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        for vuln in vulnerabilities_data:
            cursor.execute('''
                INSERT INTO vulnerabilities (vulnerability_type, flag, solution, description, difficulty, category, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', vuln + (now,))
        print("Created default vulnerabilities data")
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

if __name__ == "__main__":
    create_database()
    init_db()
