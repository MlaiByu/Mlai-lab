import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db import db_connection

def fix_session_success():
    with db_connection() as conn:
        cursor = conn.cursor()
        
        print("=== 修复开始 ===")
        
        cursor.execute('''
            SELECT id, user_id, vulnerability_id, success FROM experiment_records
            WHERE success > 0
        ''')
        records = cursor.fetchall()
        
        fixed_count = 0
        
        for record in records:
            record_id = record['id']
            user_id = record['user_id']
            vulnerability_id = record['vulnerability_id']
            record_success = record.get('success', 0)
            
            cursor.execute('''
                SELECT COUNT(*) as success_count 
                FROM experiment_sessions 
                WHERE user_id = %s AND vulnerability_id = %s AND success = 1
            ''', (user_id, vulnerability_id))
            session_success_count = cursor.fetchone()['success_count']
            
            if record_success > session_success_count:
                remaining = record_success - session_success_count
                
                cursor.execute('''
                    SELECT id, session_id 
                    FROM experiment_sessions 
                    WHERE user_id = %s AND vulnerability_id = %s AND success = 0
                    ORDER BY start_time DESC
                    LIMIT %s
                ''', (user_id, vulnerability_id, remaining))
                
                sessions_to_fix = cursor.fetchall()
                
                for session in sessions_to_fix:
                    session_id = session['session_id']
                    cursor.execute('''
                        UPDATE experiment_sessions 
                        SET success = 1 
                        WHERE session_id = %s
                    ''', (session_id,))
                    fixed_count += 1
                    print(f"修复会话: session_id={session_id}, user_id={user_id}, vulnerability_id={vulnerability_id}")
        
        conn.commit()
        print(f"=== 修复完成 ===")
        print(f"共修复 {fixed_count} 个会话")

if __name__ == '__main__':
    fix_session_success()