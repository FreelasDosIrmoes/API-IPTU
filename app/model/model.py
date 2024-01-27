from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey

db = SQLAlchemy()


class Iptu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100))
    name = db.Column(db.String(100))
    send = db.Column(db.Boolean, default=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(20))
    inconsistent = db.Column(db.Boolean, default=False)
    last_message = db.Column(db.DateTime(timezone=True))
    dono = db.relationship("Dono", cascade="all,delete", uselist=False, backref="iptu")
    cobranca = db.relationship("Cobranca", cascade="all,delete", backref="iptu")
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


class Dono(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100))
    numero = db.Column(db.String(20), nullable=False)
    iptu_id = db.Column(db.Integer, ForeignKey('iptu.id'))
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


class Cobranca(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer)
    cota = db.Column(db.String(50))
    multa = db.Column(db.Float)
    outros = db.Column(db.Float)
    total = db.Column(db.Float)
    iptu_id = db.Column(db.Integer, ForeignKey('iptu.id'))
    pdf = db.Column(db.LargeBinary)
    status_boleto = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __eq__(self, other):
        if not isinstance(other, Cobranca):
            return False
        return self.total == other.total and self.cota == other.cota and self.multa == other.multa and self.ano == other.ano and self.outros == other.outros
