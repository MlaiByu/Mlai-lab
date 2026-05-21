import requests
import time
import threading
import random

BASE_URL = "http://localhost:8000"

def login_as_student():
    login_data = {"username": "student1", "password": "123456"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["user"]["token"]
    return None

def test_vulnerability_list(token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/experiment/vulnerabilities", headers=headers)
    elapsed = (time.time() - start) * 1000
    return response.status_code == 200, elapsed

def test_user_list(token):
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    response = requests.get(f"{BASE_URL}/api/users/list", headers=headers)
    elapsed = (time.time() - start) * 1000
    return response.status_code == 200, elapsed

def test_experiment_start(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"user_id": 3, "vulnerability_id": 1}
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/experiment/start", headers=headers, json=data)
    elapsed = (time.time() - start) * 1000
    return response.status_code == 200, elapsed

def run_concurrent_tests(concurrent_count, test_function, token, results):
    for _ in range(concurrent_count):
        success, elapsed = test_function(token)
        results.append({"success": success, "elapsed": elapsed})

def performance_test():
    print("="*60)
    print("性能测试执行报告")
    print("="*60)
    
    student_token = login_as_student()
    if not student_token:
        print("❌ 学生登录失败")
        return
    
    print("✓ 学生登录成功")
    print()
    
    # 获取管理员Token
    admin_token = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "password"}).json()["user"]["token"]
    print("✓ 管理员登录成功")
    print()
    
    test_cases = [
        {"name": "漏洞列表查询", "function": test_vulnerability_list, "token": None, "iterations": 50},
        {"name": "用户列表查询", "function": test_user_list, "token": admin_token, "iterations": 30},
        {"name": "实验启动", "function": test_experiment_start, "token": student_token, "iterations": 10},
    ]
    
    for test_case in test_cases:
        print(f"测试: {test_case['name']}")
        print("-" * 40)
        
        results = []
        threads = []
        
        # 并发测试
        concurrent_counts = [10, 20, 30]
        for concurrency in concurrent_counts:
            results.clear()
            for _ in range(concurrency):
                t = threading.Thread(target=lambda: results.append(test_case["function"](test_case["token"])))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            successful = sum(1 for r in results if r[0])
            avg_time = sum(r[1] for r in results) / len(results)
            min_time = min(r[1] for r in results)
            max_time = max(r[1] for r in results)
            
            print(f"并发 {concurrency} 用户:")
            print(f"  成功: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
            print(f"  平均耗时: {avg_time:.2f} ms")
            print(f"  最小耗时: {min_time:.2f} ms")
            print(f"  最大耗时: {max_time:.2f} ms")
        
        print()
    
    print("="*60)
    print("性能测试完成")
    print("="*60)

if __name__ == "__main__":
    performance_test()