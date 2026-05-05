import pymysql
import datetime
from config import Config

def fix_database():
    conn = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    
    print("Fixing database structure and data...")
    
    # Step 1: Check if columns exist before adding
    cursor.execute("DESCRIBE vulnerabilities")
    columns = {row['Field'] for row in cursor.fetchall()}
    
    if 'vulnerability_type' not in columns:
        try:
            cursor.execute("ALTER TABLE vulnerabilities ADD COLUMN vulnerability_type VARCHAR(50) AFTER id")
            print("Added vulnerability_type column")
        except Exception as e:
            print(f"Error adding vulnerability_type: {e}")
    else:
        print("vulnerability_type column already exists")
    
    if 'difficulty' not in columns:
        try:
            cursor.execute("ALTER TABLE vulnerabilities ADD COLUMN difficulty VARCHAR(20) NOT NULL DEFAULT 'easy' AFTER description")
            print("Added difficulty column")
        except Exception as e:
            print(f"Error adding difficulty: {e}")
    else:
        print("difficulty column already exists")
    
    # Step 2: Update existing data to set vulnerability_type (copy from type column)
    cursor.execute("DESCRIBE vulnerabilities")
    new_columns = {row['Field'] for row in cursor.fetchall()}
    
    cursor.execute("SELECT id, type, name FROM vulnerabilities")
    vulns = cursor.fetchall()
    
    for vuln in vulns:
        # Copy type to vulnerability_type
        if 'vulnerability_type' in new_columns:
            cursor.execute(
                "UPDATE vulnerabilities SET vulnerability_type = %s WHERE id = %s",
                (vuln['type'], vuln['id'])
            )
            print(f"Updated vulnerability {vuln['id']}: {vuln['name']}")
    
    # Step 3: Set difficulty levels based on name
    difficulty_map = {
        'SQL注入-入门': 'easy',
        'SQL注入-中级': 'medium',
        'SQL注入-高级': 'hard',
        '反射型XSS': 'easy',
        '存储型XSS': 'medium',
        'DOM型XSS': 'medium',
        'PHP反序列化': 'hard',
        'Python反序列化': 'hard',
        '文件上传': 'medium',
        'CSRF-Easy': 'easy',
        'CSRF-Hard': 'hard'
    }
    
    cursor.execute("SELECT id, name FROM vulnerabilities")
    vulns = cursor.fetchall()
    
    for vuln in vulns:
        difficulty = difficulty_map.get(vuln['name'], 'medium')
        cursor.execute(
            "UPDATE vulnerabilities SET difficulty = %s WHERE id = %s",
            (difficulty, vuln['id'])
        )
        print(f"Set difficulty for {vuln['name']}: {difficulty}")
    
    # Step 4: Add missing vulnerabilities (CSRF ones)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    missing_vulns = [
        ('CSRF-Easy', 'Mlai{CSRF-Easy-Success}', '1. 这是一个无任何CSRF防护的漏洞\n2. 构造一个恶意页面，包含自动提交的表单\n3. 表单的action指向目标URL\n4. 输入框中填入要修改的数据（密码改成hacked!）\n5. 诱骗已登录的用户访问恶意页面\n6. 访问?get_flag=1获取flag', 'CSRF跨站请求伪造漏洞，无任何防护', 'easy', 'csrf'),
        ('CSRF-Hard', 'Mlai{CSRF-Hard-Success}', '1. 这是一个有Referer检查的CSRF漏洞\n2. Referer检查使用了strpos($referer, $host) !== false\n3. 可以通过构造URL子域名或路径来绕过\n4. 如：构造http://target-server.attacker.com 或者 http://attacker.com/target-server.com\n5. 完成任务：转账999元给attacker + 修改密码为hacked! + 访问?get_flag=1', 'CSRF跨站请求伪造漏洞，有Referer检查但可绕过', 'hard', 'csrf')
    ]
    
    for vuln_type, flag, solution, description, difficulty, category in missing_vulns:
        cursor.execute('SELECT id FROM vulnerabilities WHERE vulnerability_type = %s OR name = %s', (vuln_type, vuln_type))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute('''
                INSERT INTO vulnerabilities (name, type, vulnerability_type, flag, solution, description, difficulty, category, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (vuln_type, vuln_type, vuln_type, flag, solution, description, difficulty, category, now))
            print(f"Added missing vulnerability: {vuln_type}")
        else:
            print(f"Vulnerability already exists: {vuln_type}")
    
    conn.commit()
    conn.close()
    
    print("Database fixed successfully!")

if __name__ == "__main__":
    fix_database()
