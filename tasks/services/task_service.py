from database.connection import get_db
from utils.helpers import generate_task_number
from datetime import datetime

def create_task(data):
    valid_categories = ['plumbing', 'electricity', 'cleaning', 'elevator', 'other']
    if data.get('category') not in valid_categories:
        return {'success': False, 'message': 'Некорректная категория'}, 400
    
    number = generate_task_number()
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO tasks (number, accountId, category, title, description, createdAt)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (number, data['accountId'], data['category'], data['title'], data.get('description'), datetime.now().isoformat()))
        task_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO history (task_id, timestamp, action, user)
            VALUES (?, ?, ?, ?)
        ''', (task_id, datetime.now().isoformat(), 'created', 'system'))
        db.commit()
    return get_task_by_id(task_id)

def get_tasks(args):
    query = 'SELECT * FROM tasks WHERE 1=1'
    params = []
    
    if 'q' in args:
        query += ' AND number LIKE ?'
        params.append(f"{args['q']}%")
    
    if 'date' in args:
        query += ' AND date(createdAt) = ?'
        params.append(args['date'])
    
    if 'status' in args and args['status'] in ['new', 'in_progress', 'completed', 'confirmed']:
        query += ' AND status = ?'
        params.append(args['status'])
    
    if 'category' in args:
        query += ' AND category = ?'
        params.append(args['category'])
    
    take = int(args.get('take', 50))
    skip = int(args.get('skip', 0))
    query += ' LIMIT ? OFFSET ?'
    params.extend([take, skip])
    
    tasks = []
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(query, params)
        for row in cursor.fetchall():
            tasks.append(get_task_by_id(row['id']))
    return tasks

def get_task_by_id(task_id):
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        if not task:
            return None
        
        cursor.execute('SELECT * FROM task_assignees WHERE task_id = ?', (task_id,))
        assignee = cursor.fetchone()
        assignee_data = None
        if assignee:
            cursor.execute('SELECT * FROM executors WHERE id = ?', (assignee['executor_id'],))
            assignee_data = dict(cursor.fetchone())
        
        cursor.execute('SELECT * FROM attachments WHERE task_id = ?', (task_id,))
        attachments = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM history WHERE task_id = ?', (task_id,))
        history = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM comments WHERE task_id = ?', (task_id,))
        comments = [dict(row) for row in cursor.fetchall()]
        
        return {
            'id': task['id'],
            'number': task['number'],
            'accountId': task['accountId'],
            'category': task['category'],
            'priority': task['priority'],
            'title': task['title'],
            'description': task['description'],
            'status': task['status'],
            'createdAt': task['createdAt'],
            'assignee': assignee_data,
            'attachments': attachments,
            'history': history,
            'comments': comments
        }