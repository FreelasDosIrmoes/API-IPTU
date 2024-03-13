import threading

from flask import Flask, request, make_response, json
from app.model.model import *
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from datetime import datetime
from flasgger import Swagger
from flask_cors import CORS

load_dotenv()
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')
API_MSG = os.getenv('API_MSG')

app_flask = Flask(__name__)
app_flask.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app_flask.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_flask.config['SWAGGER'] = {
    'title': 'API IPTU',
    'uiversion': 3,
    'version': '1.0',
}
db.init_app(app_flask)
migrate = Migrate(app_flask, db)
cors = CORS(app_flask, resources={r"/api/*": {"origins": "*"}})

swagger = Swagger(app=app_flask)

from app import views