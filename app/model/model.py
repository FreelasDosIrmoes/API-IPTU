from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
db = SQLAlchemy()

class Iptu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(10), unique=True, nullable=False)
    address = db.Column(db.String(100))
    dono = db.relationship("Dono", uselist=False, backref="iptu")
    cobranca = db.relationship("Cobranca", backref="iptu")
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Dono(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    numero = db.Column(db.String(20), unique=True, nullable=False)
    iptu_id = db.Column(db.Integer, ForeignKey('iptu.id'))
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Cobranca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer)
    cota = db.Column(db.Float)
    multa = db.Column(db.Float)
    outros = db.Column(db.Float)
    total = db.Column(db.Float)
    iptu_id = db.Column(db.Integer, ForeignKey('iptu.id'))
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
