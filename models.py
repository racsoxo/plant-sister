from extensions import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class Planta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_comun = db.Column(db.String(100), nullable=False)
    nombre_cientifico = db.Column(db.String(100))
    nombre_alias = db.Column(db.String(100))
    imagen = db.Column(db.String(200))
    frecuencia_riego = db.Column(db.Integer, default=7)  # días entre riegos
    ultimo_riego = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_identificacion = db.Column(db.Float)
    wiki_summary = db.Column(db.Text)
    wiki_url = db.Column(db.String(200))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def dias_hasta_riego(self):
        if not self.ultimo_riego:
            return 0
        
        dias_transcurridos = (datetime.utcnow() - self.ultimo_riego).days
        return self.frecuencia_riego - dias_transcurridos

    @property
    def necesita_riego(self):
        return self.dias_hasta_riego <= 0

class Riego(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planta_id = db.Column(db.Integer, db.ForeignKey('planta.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    plantas = db.relationship('Planta', backref='usuario', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
