## Realiza la carga de toda la base de datos y del modelo ML
import os

filepath = os.path.dirname(os.path.abspath(__file__)) + '/database.sqlite'
try:
    os.remove(filepath)
except OSError:
    pass
filepath2 = os.path.dirname(os.path.abspath(__file__)) + '/model.joblib'
try:
    os.remove(filepath2)
except OSError:
    pass


import load_data

load_data.load_data()
load_data.load_ml_model()