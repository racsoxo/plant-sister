import torch
import torch.nn as nn
import torchvision.models as models

class PlantRecognitionModel:
    def __init__(self):
        # Usar ResNet pre-entrenado como base
        self.model = models.resnet50(pretrained=True)
        num_ftrs = self.model.fc.in_features
        
        # Modificar la última capa para nuestras clases de plantas
        self.model.fc = nn.Linear(num_ftrs, 100)  # 100 tipos de plantas diferentes
        
        # Cargar pesos pre-entrenados específicos para plantas (cuando los tengamos)
        # self.model.load_state_dict(torch.load('plant_model_weights.pth'))
        
        self.model.eval()
        
        # Mapeo de índices a nombres de plantas
        self.plant_names = {
            0: "Monstera deliciosa",
            1: "Pothos",
            2: "Sansevieria",
            # ... más plantas
        }
    
    def __call__(self, x):
        return self.model(x)
    
    def get_plant_name(self, prediction):
        idx = prediction.argmax().item()
        return self.plant_names.get(idx, "Planta desconocida") 