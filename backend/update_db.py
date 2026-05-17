import pymysql
import traceback
from config import Config

def update_database():
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
        print("=== 开始数据库更新 ===\n")

        # 1. 删除 audit_logs 表
        print("1. 删除 audit_logs 表")
        try:
            cursor.execute('DROP TABLE IF EXISTS audit_logs')
            print("✓ audit_logs 表已删除（或不存在）")
        except Exception as e:
            print(f"✗ 删除失败: {e}")

        # 2. 为 experiment_sessions 表添加 success 字段
        print("\n2. 为 experiment_sessions 表添加 success 字段")
        try:
            cursor.execute('SELECT success FROM experiment_sessions LIMIT 1')
            print("✓ success 字段已存在")
        except Exception:
            cursor.execute('ALTER TABLE experiment_sessions ADD COLUMN success INTEGER NOT NULL DEFAULT 0')
            print("✓ success 字段添加成功")

        # 3. 确保 experiment_records 表的 success 字段正确
        print("\n3. 检查 experiment_records 表结构")
        try:
            cursor.execute('SHOW COLUMNS FROM experiment_records')
            columns = cursor.fetchall()
            print("✓ 列结构:")
            for col in columns:
                print(f"  - {col['Field']}: {col['Type']}")
        except Exception as e:
            print(f"✗ 检查失败: {e}")

        conn.commit()
        print("\n=== 数据库更新完成 ===")

    except Exception as e:
        print(f"\n✗ 数据库更新失败: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=========================================")
    print("  Mlai-Lab 数据库更新")
    print("=========================================")
    update_database()
