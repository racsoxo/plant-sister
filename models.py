from extensions import db
from datetime import datetime

class Planta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_comun = db.Column(db.String(100), nullable=False)
    nombre_cientifico = db.Column(db.String(100))
    nombre_alias = db.Column(db.String(100))
    imagen = db.Column(db.String(200))
    frecuencia_riego = db.Column(db.Integer, default=7)
    ultimo_riego = db.Column(db.DateTime, default=datetime.utcnow)

class Riego(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planta_id = db.Column(db.Integer, db.ForeignKey('planta.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
