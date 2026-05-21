#!/usr/bin/env python3
"""
清理实验数据脚本
删除所有：
- Docker容器
- 实验会话
- 实验记录
"""

import os
import sys
import subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db import get_db_connection
from config import Config

def cleanup_docker():
    """清理所有相关的Docker容器和资源"""
    print("=== 清理Docker容器 ===")
    
    # 查找所有mlaic_开头的容器
    result = subprocess.run(
        ['docker', 'ps', '-a', '--filter', 'name=mlaic_', '--format', '{{.ID}}'],
        capture_output=True,
        text=True
    )
    
    container_ids = result.stdout.strip().split('\n')
    container_ids = [cid for cid in container_ids if cid]
    
    if container_ids:
        print(f"找到 {len(container_ids)} 个容器，正在删除...")
        for cid in container_ids:
            try:
                subprocess.run(['docker', 'rm', '-f', cid], capture_output=True)
                print(f"  ✓ 删除容器: {cid}")
            except Exception as e:
                print(f"  ✗ 删除容器失败 {cid}: {e}")
    else:
        print("没有找到需要清理的Docker容器")
    
    # 清理相关网络和卷
    print("\n清理Docker网络和卷...")
    subprocess.run(
        ['docker', 'network', 'ls', '--filter', 'name=mlaic_', '--format', '{{.ID}}'],
        capture_output=True
    )
    subprocess.run(
        ['docker', 'volume', 'ls', '--filter', 'name=mlaic_', '--format', '{{.Name}}'],
        capture_output=True
    )
    
    print("✓ Docker清理完成\n")

def cleanup_database():
    """清理数据库中的实验数据"""
    print("=== 清理数据库 ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除实验会话
        cursor.execute("DELETE FROM experiment_sessions")
        session_count = cursor.rowcount
        print(f"✓ 删除 {session_count} 条实验会话记录")
        
        # 删除实验记录
        cursor.execute("DELETE FROM experiment_records")
        record_count = cursor.rowcount
        print(f"✓ 删除 {record_count} 条实验记录")
        
        # 重置用户分数（可选，这里不做）
        # cursor.execute("UPDATE users SET score = 0")
        
        conn.commit()
        conn.close()
        print("✓ 数据库清理完成\n")
        
        return True
    except Exception as e:
        print(f"✗ 数据库清理失败: {e}")
        return False

def main():
    print("=" * 50)
    print("开始清理实验数据")
    print("=" * 50)
    print()
    
    # 确认
    response = input("⚠️  这将删除所有实验数据！确定要继续吗？(yes/no): ")
    if response.lower() != 'yes':
        print("取消清理")
        return
    
    print()
    
    # 清理Docker
    cleanup_docker()
    
    # 清理数据库
    cleanup_database()
    
    print("=" * 50)
    print("✓ 清理完成！")
    print("=" * 50)

if __name__ == '__main__':
    main()
