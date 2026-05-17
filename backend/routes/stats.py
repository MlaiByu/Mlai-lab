from flask import Blueprint, jsonify, request, make_response
from utils.db import get_db_connection, get_all_users, get_experiment_records, get_experiment_sessions, get_user_by_id
from utils.auth import teacher_or_admin_required
import csv
import io

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/api/stats/class_overview', methods=['GET'])
@teacher_or_admin_required
def get_class_overview():
    try:
        users = get_all_users()
        students = [u for u in users if u['role'] == 'student']
        
        total_students = len(students)
        total_attempts = 0
        total_success = 0
        completed_students = 0
        
        for student in students:
            records = get_experiment_records(student['id'])
            attempts = sum(r['attempt_count'] for r in records)
            success = sum(1 for r in records if r['success'] == 1)
            total_attempts += attempts
            total_success += success
            if success > 0:
                completed_students += 1
        
        completion_rate = round(completed_students / total_students * 100, 1) if total_students > 0 else 0
        avg_success_rate = round(total_success / total_attempts * 100, 1) if total_attempts > 0 else 0
        
        return jsonify({
            "success": True,
            "data": {
                "total_students": total_students,
                "total_attempts": total_attempts,
                "total_success": total_success,
                "completed_students": completed_students,
                "completion_rate": completion_rate,
                "avg_success_rate": avg_success_rate
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@stats_bp.route('/api/stats/vulnerability_stats', methods=['GET'])
@teacher_or_admin_required
def get_vulnerability_stats():
    try:
        users = get_all_users()
        students = [u for u in users if u['role'] == 'student']
        
        vuln_stats = {}
        
        for student in students:
            records = get_experiment_records(student['id'])
            for record in records:
                vuln_id = record['vulnerability_id']
                vuln_name = record.get('name', f'vulnerability_{vuln_id}')
                if vuln_id not in vuln_stats:
                    vuln_stats[vuln_id] = {
                        'vulnerability_id': vuln_id,
                        'vulnerability_name': vuln_name,
                        'total_attempts': 0,
                        'total_success': 0,
                        'attempted_students': 0,
                        'completed_students': 0
                    }
                vuln_stats[vuln_id]['total_attempts'] += record['attempt_count']
                if record['success'] == 1:
                    vuln_stats[vuln_id]['total_success'] += 1
                if record['attempt_count'] > 0:
                    vuln_stats[vuln_id]['attempted_students'] += 1
                if record['success'] == 1:
                    vuln_stats[vuln_id]['completed_students'] += 1
        
        result = []
        for vuln_id, stats in vuln_stats.items():
            completion_rate = round(stats['completed_students'] / stats['attempted_students'] * 100, 1) if stats['attempted_students'] > 0 else 0
            success_rate = round(stats['total_success'] / stats['total_attempts'] * 100, 1) if stats['total_attempts'] > 0 else 0
            result.append({
                'vulnerability_id': vuln_id,
                'vulnerability_name': stats['vulnerability_name'],
                'attempted_students': stats['attempted_students'],
                'completed_students': stats['completed_students'],
                'total_attempts': stats['total_attempts'],
                'total_success': stats['total_success'],
                'completion_rate': completion_rate,
                'success_rate': success_rate
            })
        
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@stats_bp.route('/api/stats/student_ranking', methods=['GET'])
@teacher_or_admin_required
def get_student_ranking():
    try:
        users = get_all_users()
        students = [u for u in users if u['role'] == 'student']
        
        ranking = []
        
        for student in students:
            records = get_experiment_records(student['id'])
            total_attempts = sum(r['attempt_count'] for r in records)
            total_success = sum(1 for r in records if r['success'] == 1)
            success_rate = round(total_success / total_attempts * 100, 1) if total_attempts > 0 else 0
            
            ranking.append({
                'user_id': student['id'],
                'username': student['username'],
                'total_attempts': total_attempts,
                'total_success': total_success,
                'success_rate': success_rate,
                'completed_experiments': len([r for r in records if r['success'] == 1])
            })
        
        ranking.sort(key=lambda x: x['completed_experiments'], reverse=True)
        
        return jsonify({"success": True, "data": ranking})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@stats_bp.route('/api/stats/export_scores', methods=['GET'])
@teacher_or_admin_required
def export_scores():
    try:
        user_id = request.args.get('userId', type=int)
        
        if user_id:
            return export_single_student_progress(user_id)
        else:
            return export_all_students_scores()
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

def export_all_students_scores():
    users = get_all_users()
    students = [u for u in users if u['role'] == 'student']
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['排名', '用户名', '总尝试次数', '总成功次数', '成功率', '完成实验数'])
    
    ranking = []
    for student in students:
        records = get_experiment_records(student['id'])
        total_attempts = sum(r['attempt_count'] for r in records)
        total_success = sum(1 for r in records if r['success'] == 1)
        success_rate = round(total_success / total_attempts * 100, 1) if total_attempts > 0 else 0
        completed = len([r for r in records if r['success'] == 1])
        
        ranking.append({
            'username': student['username'],
            'total_attempts': total_attempts,
            'total_success': total_success,
            'success_rate': success_rate,
            'completed': completed
        })
    
    ranking.sort(key=lambda x: x['completed'], reverse=True)
    
    for i, student in enumerate(ranking, 1):
        writer.writerow([
            i,
            student['username'],
            student['total_attempts'],
            student['total_success'],
            f"{student['success_rate']}%",
            student['completed']
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=experiment_scores.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

def export_single_student_progress(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "message": "用户不存在"})
    
    records = get_experiment_records(user_id)
    sessions = get_experiment_sessions(user_id)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['学生信息', ''])
    writer.writerow(['用户名', user['username']])
    writer.writerow(['角色', user['role']])
    writer.writerow(['注册时间', user['created_at']])
    writer.writerow([])
    
    writer.writerow(['学习进度统计', ''])
    total_attempts = sum(r['attempt_count'] for r in records)
    total_success = sum(1 for r in records if r['success'] == 1)
    completed = len([r for r in records if r['success'] == 1])
    success_rate = round(total_success / total_attempts * 100, 1) if total_attempts > 0 else 0
    
    writer.writerow(['总尝试次数', total_attempts])
    writer.writerow(['总成功次数', total_success])
    writer.writerow(['完成实验数', completed])
    writer.writerow(['成功率', f"{success_rate}%"])
    writer.writerow([])
    
    writer.writerow(['各实验详情', '', '', ''])
    writer.writerow(['实验ID', '实验名称', '尝试次数', '状态'])
    
    for record in records:
        status = '已完成' if record['success'] == 1 else '进行中' if record['attempt_count'] > 0 else '未开始'
        writer.writerow([
            record['vulnerability_id'],
            record.get('name', ''),
            record['attempt_count'],
            status
        ])
    
    writer.writerow([])
    writer.writerow(['实验会话记录', '', '', '', '', ''])
    writer.writerow(['会话ID', '开始时间', '结束时间', '状态', '容器ID', '端口'])
    
    for session in sessions:
        status = '成功' if session['success'] == 1 else '失败' if session['end_time'] else '进行中'
        writer.writerow([
            session['session_id'],
            session['start_time'],
            session.get('end_time', ''),
            status,
            session.get('docker_container_id', ''),
            session.get('server_port', '')
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={user["username"]}_progress.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@stats_bp.route('/api/logs/experiment_operations', methods=['GET'])
@teacher_or_admin_required
def get_experiment_logs():
    try:
        user_id = request.args.get('userId', type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT * FROM experiment_sessions
                WHERE user_id = %s
                ORDER BY start_time DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT s.*, u.username 
                FROM experiment_sessions s
                JOIN users u ON s.user_id = u.id
                ORDER BY s.start_time DESC
                LIMIT 100
            ''')
        
        sessions = cursor.fetchall()
        conn.close()
        
        logs = []
        for session in sessions:
            logs.append({
                'session_id': session['session_id'],
                'user_id': session['user_id'],
                'username': session.get('username'),
                'docker_container_id': session.get('docker_container_id'),
                'server_port': session.get('server_port'),
                'start_time': session['start_time'],
                'end_time': session.get('end_time'),
                'success': session.get('success') == 1,
                'duration': calculate_duration(session['start_time'], session.get('end_time'))
            })
        
        return jsonify({"success": True, "data": logs})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

def calculate_duration(start_time, end_time):
    if not start_time or not end_time:
        return "进行中"
    try:
        from datetime import datetime
        start = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        diff = end - start
        minutes = diff.total_seconds() // 60
        seconds = diff.total_seconds() % 60
        return f"{int(minutes)}分{int(seconds)}秒"
    except:
        return "未知"

@stats_bp.route('/api/logs/user_operations/<int:user_id>', methods=['GET'])
@teacher_or_admin_required
def get_user_operations(user_id):
    try:
        sessions = get_experiment_sessions(user_id)
        
        operations = []
        for session in sessions:
            operations.append({
                'action': '开始实验' if not session.get('end_time') else '完成实验',
                'timestamp': session['start_time'] if not session.get('end_time') else session['end_time'],
                'success': session.get('success') == 1,
                'duration': calculate_duration(session['start_time'], session.get('end_time'))
            })
        
        return jsonify({"success": True, "data": operations})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
