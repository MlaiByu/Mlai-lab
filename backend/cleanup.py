#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, '/root/Mlai-lab/backend')

from utils.db import get_experiment_records, get_db_connection, get_experiment_sessions
from datetime import datetime

def cleanup_expired_sessions():
    """清理超过1小时的实验会话并停止相关容器"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, user_id, session_id, vulnerability_type, start_time FROM experiment_sessions WHERE end_time IS NULL")
    sessions = cursor.fetchall()

    cleaned = 0
    for session in sessions:
        session_id = session['session_id']
        start_time = session['start_time']
        user_id = session['user_id']
        vuln_type = session['vulnerability_type']

        try:
            start = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
            elapsed = (datetime.now() - start).total_seconds()

            if elapsed > 3600:
                import subprocess
                result = subprocess.run(
                    f"docker ps -q --filter label=mlai-lab-session={session_id}",
                    shell=True, capture_output=True, text=True
                )

                if result.stdout.strip():
                    subprocess.run(
                        f"docker rm -f $(docker ps -q --filter label=mlai-lab-session={session_id})",
                        shell=True
                    )

                cursor.execute(
                    "UPDATE experiment_sessions SET end_time = %s, success = 0 WHERE id = %s",
                    (datetime.now().strftime('%Y-%m-%d %H:%M'), session['id'])
                )

                cursor.execute(
                    "UPDATE experiment_records SET is_expired = 1 WHERE user_id = %s AND vulnerability_type = %s",
                    (user_id, vuln_type)
                )

                cleaned += 1
        except Exception as e:
            print(f"Error cleaning session {session_id}: {e}")

    conn.commit()
    conn.close()

    if cleaned > 0:
        print(f"Cleaned {cleaned} expired sessions")
    return cleaned

if __name__ == "__main__":
    cleanup_expired_sessions()
