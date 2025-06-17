from flask import Flask
from flask_restx import Api
from config import Config
from routes.task_routes import ns as tasks_namespace
from database.connection import init_db

app = Flask(__name__)
api = Api(app, version='1.0', title='Tasks API', description='API для управления заявками')

# Инициализация БД
init_db()

# Регистрируем namespace под префиксом /api
api.add_namespace(tasks_namespace, path='/api/tasks')

if __name__ == '__main__':
    app.run(
        host=Config.HOST, 
        port=Config.PORT, 
        debug=Config.DEBUG
    )
