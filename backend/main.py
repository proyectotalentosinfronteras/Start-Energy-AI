from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import joblib

app = FastAPI(
    title="Start Energy AI - API de Optimización Energética",
    description="Backend dinámico con predicciones de Machine Learning y optimización PVPC",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde cualquier origen para desarrollo local
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de rutas de archivos
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "backend" / "models" / "predictor_solar.joblib"
DATA_PATH = BASE_DIR / "data" / "processed" / "energia_limpia.csv"

# Cargar el modelo entrenado al inicializar el servidor
if MODEL_PATH.exists():
    modelo_solar = joblib.load(MODEL_PATH)
    print("✅ Inteligencia Artificial 'predictor_solar.joblib' cargada con éxito en memoria.")
else:
    modelo_solar = None
    print("⚠️ Alerta: No se encontró el binario del modelo. El endpoint de predicciones fallará.")

# Estructura de datos requerida para el endpoint predictivo (Validación de tipos de datos)
class PeticionPrediccion(BaseModel):
    hora: int
    mes: int
    dia_semana: int
    pvgis_meteo_var_0: float
    pvgis_meteo_var_1: float
    tmed: float
    sol: float

@app.get("/")
def ruta_raiz():
    return {"status": "online", "proyecto": "Start Energy AI"}

# Endpoint 1: Retornar el histórico unificado de consumos y generación para pintar las gráficas
@app.get("/api/v1/dashboard-data")
def obtener_datos_dashboard():
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Archivo de datos procesados no encontrado.")
    
    # Cargamos las últimas 24 horas registradas para simular el panel diario en tiempo real
    df = pd.read_csv(DATA_PATH)
    ultimas_horas = df.tail(24).fillna(0).to_dict(orient="records")
    
    return {
        "status": "success",
        "total_registros": len(ultimas_horas),
        "data": ultimas_horas
    }

# Endpoint 2: Recibir variables de clima actuales desde el HTML y ejecutar la inferencia de la IA
@app.post("/api/v1/predict")
def predecir_generacion(datos: PeticionPrediccion):
    if modelo_solar is None:
        raise HTTPException(status_code=500, detail="El motor de Machine Learning no está operativo.")
    
    # Convertimos los datos JSON de entrada en una estructura tabular compatible con Scikit-Learn
    input_data = pd.DataFrame([{
        'hora': datos.hora,
        'mes': datos.mes,
        'dia_semana': datos.dia_semana,
        'pvgis_meteo_var_0': datos.pvgis_meteo_var_0,
        'pvgis_meteo_var_1': datos.pvgis_meteo_var_1,
        'tmed': datos.tmed,
        'sol': datos.sol
    }])
    
    # Ejecutamos la predicción con el Random Forest
    prediccion_kwh = modelo_solar.predict(input_data)[0]
    
    return {
        "status": "success",
        "generacion_estimada_kwh": round(float(prediccion_kwh), 3)
    }
