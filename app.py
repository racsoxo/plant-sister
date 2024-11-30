from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import os
from extensions import db
from models import Planta, Riego, Usuario
from datetime import datetime
import torch
from torchvision import transforms
from plant_recognition import PlantRecognitionModel  # Crearemos este módulo

app = Flask(__name__)
CORS(app)

# Configuración
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plantsister.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Importante para sessions

# Inicializar extensiones
db.init_app(app)

# Cargar modelo de reconocimiento
model = PlantRecognitionModel()

# Asegurar que existe el directorio de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    plantas = Planta.query.all()
    return render_template('index.html', plantas=plantas)

@app.route('/buscar_planta')
def buscar_planta():
    try:
        nombre = request.args.get('nombre', '').lower()
        if not nombre or len(nombre) < 3:
            return jsonify([])
            
        # Lista de plantas conocidas (esto podría venir de una base de datos real)
        plantas_conocidas = {
            'monstera': {
                'nombre_comun': 'Monstera',
                'nombre_cientifico': 'Monstera deliciosa',
                'frecuencia_riego': 'Cada 7-10 días',
            },
            'pothos': {
                'nombre_comun': 'Pothos',
                'nombre_cientifico': 'Epipremnum aureum',
                'frecuencia_riego': 'Cada 7-14 días',
            },
            'lengua': {
                'nombre_comun': 'Lengua de suegra',
                'nombre_cientifico': 'Sansevieria trifasciata',
                'frecuencia_riego': 'Cada 14-21 días',
            }
        }
        
        # Buscar coincidencias
        resultados = []
        for key, planta in plantas_conocidas.items():
            if (nombre in key.lower() or 
                nombre in planta['nombre_comun'].lower() or 
                nombre in planta['nombre_cientifico'].lower()):
                resultados.append(planta)
        
        if not resultados:
            return jsonify({'error': 'No se encontraron plantas con ese nombre'}), 404
            
        return jsonify(resultados)
        
    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/procesar_imagen', methods=['POST'])
def procesar_imagen():
    try:
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se envió ninguna imagen'}), 400
            
        archivo = request.files['imagen']
        if not archivo:
            return jsonify({'error': 'Archivo vacío'}), 400
            
        # Procesar y guardar imagen
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        imagen = Image.open(archivo)
        imagen = imagen.convert('RGB')
        imagen.thumbnail((800, 800))
        imagen.save(filepath, 'JPEG', quality=85)
        
        # Preparar imagen para el modelo
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
        
        img_tensor = transform(imagen).unsqueeze(0)
        
        # Realizar predicción
        with torch.no_grad():
            prediction = model(img_tensor)
            planta_identificada = model.get_plant_name(prediction)
            confidence = float(prediction.max())
            
        return jsonify({
            'planta': planta_identificada,
            'confidence': confidence,
            'imagen_path': filename
        })
            
    except Exception as e:
        print(f"Error en identificación: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/guardar_planta', methods=['POST'])
def guardar_planta():
    try:
        datos = request.get_json()
        
        if not datos.get('alias'):
            return jsonify({'error': 'El alias es requerido'}), 400

        # Convertir frecuencia_riego a días (por ejemplo: "Cada 7 días" -> 7)
        frecuencia_texto = datos.get('frecuencia_riego', 'Cada 7 días')
        try:
            frecuencia = int(''.join(filter(str.isdigit, frecuencia_texto)))
        except:
            frecuencia = 7  # valor por defecto

        nueva_planta = Planta(
            nombre_comun=datos.get('nombre_comun', 'Planta ejemplo'),
            nombre_cientifico=datos.get('nombre_cientifico', 'Ejemplus plantus'),
            nombre_alias=datos['alias'],
            imagen=datos.get('imagen', ''),
            frecuencia_riego=frecuencia,
            ultimo_riego=datetime.utcnow(),
            ultima_identificacion=datos.get('confidence', 0),
            wiki_summary=datos.get('summary', ''),
            wiki_url=datos.get('url', '')
        )
        
        db.session.add(nueva_planta)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Planta guardada con éxito',
            'id': nueva_planta.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar planta: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/guardar_imagen', methods=['POST'])
def guardar_imagen():
    try:
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se envió ninguna imagen'}), 400
            
        archivo = request.files['imagen']
        if not archivo:
            return jsonify({'error': 'Archivo vacío'}), 400
            
        if archivo:
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Guardar y procesar imagen
            imagen = Image.open(archivo)
            imagen = imagen.convert('RGB')
            imagen.thumbnail((800, 800))
            imagen.save(filepath, 'JPEG', quality=85)
            
            return jsonify({
                'filename': filename,
                'message': 'Imagen guardada correctamente'
            }), 200
            
    except Exception as e:
        print(f"Error al guardar imagen: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/registro', methods=['POST'])
def registro():
    try:
        datos = request.get_json()
        
        if Usuario.query.filter_by(email=datos['email']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
            
        nuevo_usuario = Usuario(
            nombre=datos['nombre'],
            email=datos['email'],
            password=datos['password']  # Asegúrate de hashear la contraseña
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        session['user_id'] = nuevo_usuario.id
        
        return jsonify({'mensaje': 'Usuario registrado con éxito'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host='127.0.0.1', port=8080, debug=True)
