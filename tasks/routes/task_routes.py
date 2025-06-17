from flask import request 
from flask_restx import Namespace, Resource
from services.task_service import create_task, get_tasks 
from swagger.models import register_models

ns = Namespace('tasks', description='Операции с заявками')

models = register_models(ns)
task_model = models['task_model']
task_response_model = models['task_response_model']
status_model = models['status_model']
assign_model = models['assign_model']
comment_model = models['comment_model']
rate_model = models['rate_model']
executor_model = models['executor_model']
executor_create_model = models['executor_create_model']

@ns.route('')
class TasksList(Resource):
    @ns.expect(task_model)
    @ns.marshal_with(task_response_model)
    def post(self):
        """Создание заявки"""
        return create_task(request.json)

    @ns.marshal_list_with(task_response_model)
    def get(self):
        """Список заявок с фильтрами"""
        return get_tasks(request.args)
