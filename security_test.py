import requests
import json

BASE_URL = "http://localhost:8000"

def test_permission_bypass():
    print("="*50)
    print("1. 权限绕过测试")
    print("="*50)
    
    # 学生登录
    login_data = {"username": "student1", "password": "123456"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        student_token = response.json()["user"]["token"]
        print("✓ 学生登录成功")
    else:
        print("✗ 学生登录失败")
        return
    
    # 测试学生访问用户列表
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(f"{BASE_URL}/api/users/list", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if not result["success"] and "权限" in result["message"]:
            print("✓ [测试1] 学生访问用户列表 - 权限控制正常")
        else:
            print("✗ [测试1] 学生访问用户列表 - 存在权限绕过漏洞")
    else:
        print("✓ [测试1] 学生访问用户列表 - 返回非200状态码")
    
    # 测试学生创建用户
    create_data = {"username": "hacker", "password": "123456", "role": "admin"}
    response = requests.post(f"{BASE_URL}/api/users/create", headers=headers, json=create_data)
    if response.status_code == 200:
        result = response.json()
        if not result["success"] and "权限" in result["message"]:
            print("✓ [测试2] 学生创建用户 - 权限控制正常")
        else:
            print("✗ [测试2] 学生创建用户 - 存在权限绕过漏洞")
    else:
        print("✓ [测试2] 学生创建用户 - 返回非200状态码")

def test_sql_injection():
    print("\n" + "="*50)
    print("2. SQL注入测试")
    print("="*50)
    
    # 测试登录接口SQL注入
    injection_data = {"username": "admin' OR '1'='1", "password": "anypassword"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=injection_data)
    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            print("✓ [测试3] 登录接口SQL注入 - 注入被拦截")
        else:
            print("✗ [测试3] 登录接口SQL注入 - 存在SQL注入漏洞")
    else:
        print("✓ [测试3] 登录接口SQL注入 - 返回非200状态码")
    
    # 测试注册接口SQL注入
    injection_data = {"username": "testuser' --", "password": "123456"}
    response = requests.post(f"{BASE_URL}/api/auth/register", json=injection_data)
    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            print("✓ [测试4] 注册接口SQL注入 - 注入被拦截")
        else:
            print("✗ [测试4] 注册接口SQL注入 - 存在SQL注入漏洞")
    else:
        print("✓ [测试4] 注册接口SQL注入 - 返回非200状态码")

def test_xss_attack():
    print("\n" + "="*50)
    print("3. XSS攻击测试")
    print("="*50)
    
    # 测试注册接口XSS
    xss_data = {"username": "<script>alert('xss')</script>", "password": "123456"}
    response = requests.post(f"{BASE_URL}/api/auth/register", json=xss_data)
    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            print("✓ [测试5] 注册接口XSS - 攻击被拦截")
        else:
            print("✗ [测试5] 注册接口XSS - 存在XSS漏洞")
    else:
        print("✓ [测试5] 注册接口XSS - 返回非200状态码")
    
    # 测试图片标签XSS
    xss_data = {"username": '<img src=x onerror=alert(document.cookie)>', "password": "123456"}
    response = requests.post(f"{BASE_URL}/api/auth/register", json=xss_data)
    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            print("✓ [测试6] 图片标签XSS - 攻击被拦截")
        else:
            print("✗ [测试6] 图片标签XSS - 存在XSS漏洞")
    else:
        print("✓ [测试6] 图片标签XSS - 返回非200状态码")

def test_csrf():
    print("\n" + "="*50)
    print("4. CSRF测试")
    print("="*50)
    
    # 测试无Token请求
    response = requests.get(f"{BASE_URL}/api/users/list")
    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            print("✓ [测试7] 无Token请求 - CSRF防护有效")
        else:
            print("✗ [测试7] 无Token请求 - 存在CSRF漏洞")
    else:
        print("✓ [测试7] 无Token请求 - 返回非200状态码")
    
    # 测试无效Token请求
    headers = {"Authorization": "Bearer invalid_token_123"}
    response = requests.get(f"{BASE_URL}/api/users/list", headers=headers)
    if response.status_code == 200:
        result = response.json()
        if not result["success"]:
            print("✓ [测试8] 无效Token请求 - Token验证有效")
        else:
            print("✗ [测试8] 无效Token请求 - Token验证存在漏洞")
    else:
        print("✓ [测试8] 无效Token请求 - 返回非200状态码")

def test_container_isolation():
    print("\n" + "="*50)
    print("5. 容器隔离测试")
    print("="*50)
    print("⚠️  容器隔离测试需要手动检查运行中的容器")
    print("建议测试项:")
    print("  - Docker Socket挂载检测")
    print("  - 容器运行用户权限")
    print("  - 宿主机目录访问限制")
    print("  - 容器间网络隔离")

def main():
    print("="*50)
    print("安全测试执行报告")
    print("="*50)
    
    test_permission_bypass()
    test_sql_injection()
    test_xss_attack()
    test_csrf()
    test_container_isolation()
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)

if __name__ == "__main__":
    main()