# ☀️ Start Energy AI: Optimización y Predicción de Generación Fotovoltaica

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success.svg" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

## 🚀 Descripción del Proyecto
**Start Energy AI** es una solución inteligente diseñada para hogares y comunidades con autoconsumo fotovoltaico. Combina el análisis de series temporales, modelos de Machine Learning y una interfaz web interactiva para predecir la generación de energía solar, anticipar excedentes y optimizar el consumo eléctrico según los precios del mercado regulado (PVPC).

---

## 🛠️ Arquitectura del Proyecto
```text
Start-Energy-AI/
│
├── data/                  # Datasets maestros (Simulados y Reales REE/AEMET)
├── notebooks/             # Pipeline analítico modular
│   ├── 01_ETL.ipynb
│   ├── 02_EDA.ipynb
│   ├── 03_Feature_Engineering.ipynb
│   ├── 04_Modelado.ipynb
│   └── 05_Evaluacion.ipynb
├── src/                   # Scripts de Python reutilizables
├── index.html             # Dashboard Web Interactivo (Frontend)
└── README.md