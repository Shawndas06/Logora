from flask_restx import fields

def register_models(api):
    task_model = api.model('TaskCreate', {
        'accountId': fields.Integer(required=True, description='ID лицевого счета'),
        'category': fields.String(required=True, description='Категория заявки',
                                  enum=['plumbing', 'electricity', 'cleaning', 'elevator', 'other']),
        'title': fields.String(required=True, description='Заголовок заявки'),
        'description': fields.String(description='Описание заявки'),
    })

    task_response_model = api.model('TaskResponse', {
        'id': fields.Integer,
        'number': fields.String,
        'accountId': fields.Integer,
        'category': fields.String,
        'priority': fields.String,
        'title': fields.String,
        'description': fields.String,
        'status': fields.String,
        'createdAt': fields.String,
        'assignee': fields.Raw,
        'attachments': fields.List(fields.Raw),
        'history': fields.List(fields.Raw),
        'comments': fields.List(fields.Raw),
    })

    status_model = api.model('Status', {
        'status': fields.String(required=True, description='Новый статус')
    })

    assign_model = api.model('Assign', {
        'id': fields.Integer(required=True, description='ID исполнителя')
    })

    comment_model = api.model('Comment', {
        'message': fields.String(required=True, description='Текст комментария')
    })

    rate_model = api.model('Rate', {
        'message': fields.String(description='Комментарий к оценке'),
        'point': fields.Integer(required=True, description='Оценка от 1 до 5')
    })

    executor_model = api.model('Executor', {
        'id': fields.Integer,
        'name': fields.String,
        'role': fields.String
    })

    executor_create_model = api.model('ExecutorCreate', {
        'name': fields.String(required=True, description='Имя исполнителя'),
        'role': fields.String(required=True, description='Роль исполнителя')
    })

    return {
        'task_model': task_model,
        'task_response_model': task_response_model,
        'status_model': status_model,
        'assign_model': assign_model,
        'comment_model': comment_model,
        'rate_model': rate_model,
        'executor_model': executor_model,
        'executor_create_model': executor_create_model
    }
