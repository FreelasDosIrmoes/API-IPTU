from flask import *
from app.model.model import db, Iptu
from app.service import handling_get_file

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/iptu-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

from app import views