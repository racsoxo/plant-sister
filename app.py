from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
import os
from services.plant_recognition import PlantRecognitionService

app = Flask(__name__)
CORS(app)

# Configuración
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Asegurar que existe el directorio de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar el servicio de reconocimiento
plant_recognition = PlantRecognitionService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return jsonify({
        'status': 'success',
        'message': 'La API está funcionando correctamente'
    })

@app.route('/buscar_planta')
def buscar_planta():
    try:
        nombre = request.args.get('nombre', '').lower()
        print(f"Búsqueda recibida: {nombre}")
        
        if not nombre or len(nombre) < 3:
            print("Nombre muy corto o vacío")
            return jsonify([])
            
        # Lista de plantas conocidas
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
        
        print(f"Resultados encontrados: {resultados}")
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
            
        # Guardar imagen
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Procesar imagen
        imagen = Image.open(archivo)
        imagen = imagen.convert('RGB')
        imagen.thumbnail((800, 800))
        imagen.save(filepath, 'JPEG', quality=85)
        
        # Realizar predicción
        resultados = plant_recognition.predict(imagen)
        
        if not resultados:
            return jsonify({
                'error': 'No se pudo identificar la planta en la imagen'
            }), 404
            
        # Devolver mejor coincidencia
        mejor_resultado = resultados[0]
        return jsonify({
            'planta': mejor_resultado['nombre'],
            'confidence': mejor_resultado['confidence'],
            'imagen_path': filename,
            'otras_opciones': resultados[1:]
        })
            
    except Exception as e:
        print(f"Error en identificación: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
