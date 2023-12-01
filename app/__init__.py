from flask import *
from app.model.model import *
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from app.service import *
from rpa.rpa import Automation
from utils.log import Log

load_dotenv()
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
DB_HOST = os.getenv('DB_HOST')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:postgres@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# with app.app_context():
#     db.drop_all()
#     db.create_all()

from app import views