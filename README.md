# ☀️ Start-Energy-AI
#  Optimización y Predicción de Generación Fotovoltaica
Python Version Status License

🚀 Descripción del Proyecto

> **Start Energy AI** es una solución inteligente diseñada para optimizar el consumo eléctrico y maximizar el autoconsumo fotovoltaico en hogares y comunidades, ayudando a reducir la factura de la luz mediante predicciones de inteligencia artificial y hábitos inteligentes.

> **La aplicación ayuda a los consumidores a ahorrar de forma automática analizando la **Predicción de Generación vs. Consumo (24h)**, gestionando alertas de excedentes y facilitando la interpretación de tarifas eléctricas, tanto para hogares con placas solares como para usuarios sin equipamiento previo.

---

## 🛠️ Stack Tecnológico
* **Frontend:** HTML5, CSS3 (Glassmorphism UI), JavaScript (Interactividad y manipulación del DOM).
* **Análisis de Datos / IA:** Python, Jupyter Notebooks, Modelos de Machine Learning entrenados con datos meteorológicos (AEMET).
* **Entorno de Trabajo:** Visual Studio Code, Git & GitHub.
* **Apoyo de Desarrollo:** Asistencia de IA (Claude) para la programación de lógica y optimización de código.

---

## 🛠️ Arquitectura del Proyecto
```text
Start-Energy-AI/
│
├── data/                  # Datasets maestros (Reales REE/AEMET/ESIOS/DATADIS/PVGIS)
├── notebooks/             # Notebooks (.ipynb) de análisis de datos
│   ├── 01_ETL.ipynb
│   ├── 02_EDA.ipynb
│   ├── 03_Feature_Engineering.ipynb
│   ├── 04_Modelado.ipynb
│   └── 05_Evaluacion.ipynb
├── backend/               # main.py
├── imagenes
├── processed              # energia_limpia.csv
├── raw                    # raw_json / raw energia_raw.csv
├── dashboard/             # js 
├── index.html             # Dashboard Web Interactivo (Frontend)
└── README.md              # Documentación del proyecto
# ⚡ Start Energy AI — Predicción y Consumo Inteligente

Autora: Proyecto desarrollado por Camila Rabelo como parte del Proyecto Final de Curso Data Analyst + IA Aplicada - 2026

