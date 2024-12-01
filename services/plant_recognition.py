from PIL import Image
import json
import os
import statistics

class PlantRecognitionService:
    def __init__(self):
        # Cargar base de datos de plantas
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'plant_labels.json'), 'r', encoding='utf-8') as f:
            self.plants = json.load(f)
        
    def predict(self, image):
        try:
            # Análisis básico de la imagen
            image = image.resize((100, 100))
            pixels = list(image.getdata())
            
            # Calcular color promedio
            r_values = [p[0] for p in pixels]
            g_values = [p[1] for p in pixels]
            b_values = [p[2] for p in pixels]
            
            avg_r = statistics.mean(r_values)
            avg_g = statistics.mean(g_values)
            avg_b = statistics.mean(b_values)
            
            # Simulación básica basada en el color dominante
            if avg_g > avg_r and avg_g > avg_b:  # Si domina el verde
                results = [
                    {'nombre': self.plants['0'], 'confidence': 0.85},
                    {'nombre': self.plants['1'], 'confidence': 0.75},
                    {'nombre': self.plants['2'], 'confidence': 0.65}
                ]
            else:
                results = [
                    {'nombre': self.plants['8'], 'confidence': 0.80},
                    {'nombre': self.plants['9'], 'confidence': 0.70},
                    {'nombre': self.plants['4'], 'confidence': 0.60}
                ]
            
            return results
            
        except Exception as e:
            print(f"Error en predicción: {str(e)}")
            return None 