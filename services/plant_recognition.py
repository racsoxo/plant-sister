import requests
from PIL import Image
import io
import json
import os
import base64

class PlantRecognitionService:
    def __init__(self):
        self.api_key = 'AIzaSyAt19bwnGiyHR-NgzOmQcWAVgly9BtwmoE'  # Tu clave API de Gemini
        self.api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'  # URL de la API de Gemini

    def predict(self, image):
        try:
            # Convertir la imagen a bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            # Convertir a base64
            img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')

            # Hacer la solicitud a la API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'  # Asegúrate de que la clave API esté en la cabecera
            }

            # Preparar el payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": img_base64
                            }
                        ]
                    }
                ]
            }

            response = requests.post(self.api_url, headers=headers, json=payload)

            print(f"Respuesta de la API: {response.status_code}")  # Debug print
            print(f"Contenido de la respuesta: {response.text}")  # Debug print

            if response.status_code == 200:
                return response.json()  # Devolver la respuesta JSON
            else:
                print(f"Error en la API: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            print(f"Error en predicción: {str(e)}")
            return None 