from datetime import datetime
import uuid

def generate_task_number():
    return f"TASK-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"