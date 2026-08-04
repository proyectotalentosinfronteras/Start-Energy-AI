"""
========================================================================
 START ENERGY AI - Proyecto Final
 Script de descarga y limpieza de datos multi-fuente
========================================================================

Descarga datos REALES de:
    1. REE / REData      -> demanda y generación (sin token)
    2. ESIOS (REE)        -> indicadores detallados (requiere token)
    3. AEMET OpenData      -> radiación y clima (requiere API key)
    4. PVGIS (UE)           -> radiación solar / potencial fotovoltaico (sin token)
    5. Datadis              -> consumo eléctrico por CUPS (requiere usuario/NIF)

Cada fuente se guarda en su propia carpeta dentro de /data, en CSV limpio
(y JSON crudo de respaldo), listos para tu notebook de ETL.

CÓMO USARLO
-----------
1. Instala dependencias:
       pip install requests pandas python-dotenv

2. Rellena tus credenciales en la sección CONFIGURACIÓN más abajo
   (o crea un archivo .env con las mismas variables, ver ejemplo al final).

3. Ajusta FECHA_INICIO / FECHA_FIN y LAT / LON a tu caso de estudio.

4. Ejecuta:
       python descarga_datos.py

   Puedes desactivar una fuente concreta poniendo su flag en False
   dentro de la función main().

Autor: generado con Claude para el proyecto Start Energy AI
========================================================================
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
import pandas as pd

# ======================================================================
# CONFIGURACIÓN — RELLENA AQUÍ TUS DATOS
# ======================================================================

# --- Rango de fechas para todas las descargas ---
FECHA_INICIO = "2023-01-01"   # formato YYYY-MM-DD
FECHA_FIN = "2023-01-31"      # formato YYYY-MM-DD

DATADIS_FECHA_INICIO = "2025-03-01"   # formato YYYY-MM-DD
DATADIS_FECHA_FIN = "2025-03-31"      # formato YYYY-MM-DD

# --- Coordenadas de referencia (ejemplo: Alicante) ---
LATITUD = 38.3452
LONGITUD = -0.4810

# --- ESIOS: solicita tu token a consultasios@ree.es ---
ESIOS_TOKEN = os.getenv("ESIOS_TOKEN", "233de5c1a0795f0b86c850dfebbaefcfaf65661e614f0209cbb561ba80aed114")

# --- AEMET: solicita tu API key en https://opendata.aemet.es ---
AEMET_API_KEY = os.getenv("AEMET_API_KEY", "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjYW1pYW1vcmltc3VhcmV6QGdtYWlsLmNvbSIsImp0aSI6ImE5NTY0ZmI3LTVkNTEtNDkzOS1hYWZiLTY2NzY3ZDA4NDVhNCIsImV4cCI6MTc5NDM5NzMyNywiaXNzIjoiQUVNRVQiLCJpYXQiOjE3ODU3NTczMjcsInVzZXJJZCI6ImE5NTY0ZmI3LTVkNTEtNDkzOS1hYWZiLTY2NzY3ZDA4NDVhNCIsInJvbGUiOiIifQ.MI_3sJCteFvQN3p9LaYYJG0nI4uTtkxQC4rKXkveGsA")
AEMET_ESTACION = "8025"  # Código de estación AEMET (ej. 8025 = Alicante/Elche aeropuerto)

# --- Datadis: usuario y contraseña de tu cuenta en datadis.es ---
DATADIS_NIF = os.getenv("DATADIS_NIF", "60550719E")
DATADIS_PASSWORD = os.getenv("DATADIS_PASSWORD", "Start.Energy.2026*")

# --- Carpeta raíz donde se guardan todos los datos ---
CARPETA_DATOS = Path("data")


# ======================================================================
# UTILIDADES
# ======================================================================

def crear_carpetas():
    """Crea la estructura de carpetas del proyecto."""
    subcarpetas = ["ree", "esios", "aemet", "pvgis", "datadis", "raw_json"]
    for sub in subcarpetas:
        (CARPETA_DATOS / sub).mkdir(parents=True, exist_ok=True)
    print(f"Estructura de carpetas lista en: {CARPETA_DATOS.resolve()}")


def guardar_json_crudo(nombre, data):
    """Guarda la respuesta cruda como respaldo, por si hace falta auditar."""
    ruta = CARPETA_DATOS / "raw_json" / f"{nombre}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def guardar_csv(df, carpeta, nombre):
    """Guarda un DataFrame limpio en CSV con encoding UTF-8."""
    ruta = CARPETA_DATOS / carpeta / f"{nombre}.csv"
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"  -> Guardado: {ruta} ({len(df)} filas)")
    return ruta


# ======================================================================
# 1. REE / REData API  (sin token)
# ======================================================================

def descargar_ree(categoria, widget, nombre_archivo, time_trunc="hour"):
    """
    Descarga un widget de la REData API de REE.
    Documentación: https://www.ree.es/es/apidatos
    """
    print(f"\n[REE] Descargando {categoria}/{widget} ...")
    url = f"https://apidatos.ree.es/es/datos/{categoria}/{widget}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    params = {
        "start_date": f"{FECHA_INICIO}T00:00",
        "end_date": f"{FECHA_FIN}T23:59",
        "time_trunc": time_trunc,
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        guardar_json_crudo(f"ree_{nombre_archivo}", data)

        registros = []
        for bloque in data.get("included", []):
            titulo = bloque["attributes"]["title"]
            tipo = bloque.get("type", "")
            for punto in bloque["attributes"]["values"]:
                registros.append({
                    "categoria": categoria,
                    "serie": titulo,
                    "tipo": tipo,
                    "fecha": punto["datetime"],
                    "valor": punto["value"],
                    "porcentaje": punto.get("percentage"),
                })

        df = pd.DataFrame(registros)
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"], utc=True)
            df = df.sort_values("fecha")
        return guardar_csv(df, "ree", nombre_archivo)

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR REE] {e}")
        return None


# ======================================================================
# 2. ESIOS API (requiere token)
# ======================================================================

def descargar_esios_indicador(indicador_id, nombre_archivo):
    """
    Descarga un indicador concreto de ESIOS.
    Indicadores útiles:
      1293 -> Demanda real
      551  -> Generación eólica
      549  -> Generación solar fotovoltaica
      600  -> Precio spot mercado diario
    Lista completa: https://api.esios.ree.es/indicators
    """
    if ESIOS_TOKEN.startswith("233de5c1a0795f0b86c850dfebbaefcfaf65661e614f0209cbb561ba80aed114"):
        print(f"\n[ESIOS] Saltando indicador {indicador_id}: falta configurar ESIOS_TOKEN")
        return None

    print(f"\n[ESIOS] Descargando indicador {indicador_id} ...")
    url = f"https://api.esios.ree.es/indicators/{indicador_id}"
    headers = {
        "Accept": "application/json; application/vnd.esios-api-v2+json",
        "Content-Type": "application/json",
        "x-api-key": ESIOS_TOKEN,
    }
    params = {
        "start_date": f"{FECHA_INICIO}T00:00:00",
        "end_date": f"{FECHA_FIN}T23:59:00",
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        guardar_json_crudo(f"esios_{nombre_archivo}", data)

        valores = data.get("indicator", {}).get("values", [])
        df = pd.DataFrame(valores)
        if not df.empty:
            df = df.rename(columns={"datetime": "fecha", "value": "valor"})
            df["fecha"] = pd.to_datetime(df["fecha"], utc=True)
            df = df[["fecha", "valor", "geo_name"]].sort_values("fecha")
        return guardar_csv(df, "esios", nombre_archivo)

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR ESIOS] {e}")
        return None


# ======================================================================
# 3. AEMET OpenData (requiere API key)
# ======================================================================

def descargar_aemet_climatologia():
    """
    Descarga la climatología diaria (incluye radiación cuando la estación
    la reporta) de una estación AEMET en el rango de fechas configurado.
    AEMET limita a series de hasta 5 años por petición; funciona en tramos.
    """
    if AEMET_API_KEY.startswith("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjYW1pYW1vcmltc3VhcmV6QGdtYWlsLmNvbSIsImp0aSI6ImE5NTY0ZmI3LTVkNTEtNDkzOS1hYWZiLTY2NzY3ZDA4NDVhNCIsImV4cCI6MTc5NDM5NzMyNywiaXNzIjoiQUVNRVQiLCJpYXQiOjE3ODU3NTczMjcsInVzZXJJZCI6ImE5NTY0ZmI3LTVkNTEtNDkzOS1hYWZiLTY2NzY3ZDA4NDVhNCIsInJvbGUiOiIifQ.MI_3sJCteFvQN3p9LaYYJG0nI4uTtkxQC4rKXkveGsA"):
        print("\n[AEMET] Saltando: falta configurar AEMET_API_KEY")
        return None

    print(f"\n[AEMET] Descargando climatología estación {AEMET_ESTACION} ...")
    headers = {"api_key": AEMET_API_KEY}
    url = (
        f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/"
        f"datos/fechaini/{FECHA_INICIO}T00:00:00UTC/fechafin/{FECHA_FIN}T23:59:59UTC/"
        f"estacion/{AEMET_ESTACION}"
    )

    try:
        # Paso 1: AEMET devuelve una URL intermedia con los datos reales
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        meta = r.json()

        if meta.get("estado") != 200:
            print(f"  [AEMET] Respuesta inesperada: {meta}")
            return None

        r_datos = requests.get(meta["datos"], headers=headers, timeout=30)
        r_datos.raise_for_status()
        data = r_datos.json()
        guardar_json_crudo("aemet_climatologia", data)

        df = pd.DataFrame(data)
        return guardar_csv(df, "aemet", "climatologia_diaria")

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR AEMET] {e}")
        return None


# ======================================================================
# 4. PVGIS API (sin token)
# ======================================================================

def descargar_pvgis_radiacion():
    """
    Descarga la serie horaria de radiación e irradiancia estimada para
    las coordenadas configuradas. Usa el año completo más reciente
    disponible en PVGIS (normalmente va 1-2 años por detrás del actual).
    """
    print(f"\n[PVGIS] Descargando radiación horaria para lat={LATITUD}, lon={LONGITUD} ...")
    anio = datetime.strptime(FECHA_FIN, "%Y-%m-%d").year
    url = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"
    params = {
        "lat": LATITUD,
        "lon": LONGITUD,
        "startyear": anio,
        "endyear": anio,
        "outputformat": "json",
    }

    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        guardar_json_crudo("pvgis_radiacion", data)

        df = pd.DataFrame(data["outputs"]["hourly"])
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M", utc=True)
        df = df.rename(columns={"time": "fecha", "G(i)": "irradiancia_wm2", "T2m": "temp_2m"})

        # Filtra al rango de fechas de interés
        mask = (df["fecha"] >= FECHA_INICIO) & (df["fecha"] <= FECHA_FIN + " 23:59")
        df_filtrado = df.loc[mask].copy() if mask.any() else df

        return guardar_csv(df_filtrado, "pvgis", "radiacion_horaria")

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR PVGIS] {e}")
        return None


def descargar_pvgis_potencial_fv(potencia_kwp=1):
    """Estimación de producción fotovoltaica para una instalación de referencia."""
    print(f"\n[PVGIS] Descargando estimación PV ({potencia_kwp} kWp) ...")
    url = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"
    params = {
        "lat": LATITUD,
        "lon": LONGITUD,
        "peakpower": potencia_kwp,
        "loss": 14,
        "outputformat": "json",
    }
    try:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        guardar_json_crudo("pvgis_potencial_fv", data)

        mensual = data["outputs"]["monthly"]["fixed"]
        df = pd.DataFrame(mensual)
        return guardar_csv(df, "pvgis", "produccion_fv_mensual")

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR PVGIS PV] {e}")
        return None


# ======================================================================
# 5. Datadis (requiere usuario/NIF y contraseña)
# ======================================================================

def descargar_datadis_consumo():
    """
    Autentica contra Datadis y descarga el consumo horario de todos
    los puntos de suministro (CUPS) asociados a tu cuenta.
    """
    if DATADIS_NIF.startswith("PON_AQUI"):
        print("\n[DATADIS] Saltando: falta configurar DATADIS_NIF / DATADIS_PASSWORD")
        return None

    print("\n[DATADIS] Autenticando ...")
    try:
        r_token = requests.post(
            "https://datadis.es/nikola-auth/tokens/login",
            data={"username": DATADIS_NIF, "password": DATADIS_PASSWORD},
            timeout=30,
        )
        r_token.raise_for_status()
        token = r_token.text.strip()
        headers = {"Authorization": f"Bearer {token}"}

        # Paso 1: obtener los puntos de suministro (CUPS) disponibles
        r_supplies = requests.get(
            "https://datadis.es/api-private/api/get-supplies", headers=headers, timeout=30
        )
        r_supplies.raise_for_status()
        supplies = r_supplies.json()
        guardar_json_crudo("datadis_supplies", supplies)

        if not supplies:
            print("  [DATADIS] No se encontraron puntos de suministro en la cuenta.")
            return None

        # Paso 2: descargar consumo horario del primer CUPS encontrado
        cups = supplies[0]["cups"]
        distribuidora = supplies[0]["distributorCode"]
        inicio = FECHA_INICIO.replace("-", "")[:6]  # Datadis pide AAAA/MM
        fin = FECHA_FIN.replace("-", "")[:6]

        params = {
            "cups": cups,
            "distributorCode": distribuidora,
            "startDate": DATADIS_FECHA_INICIO[:7].replace("-", "/"),
            "endDate": DATADIS_FECHA_FIN[:7].replace("-", "/"),
            "measurementType": 0,
            "pointType": supplies[0].get("pointType", 5),
        }
        r_consumo = requests.get(
            "https://datadis.es/api-private/api/get-consumption-data",
            headers=headers, params=params, timeout=30,
        )
        r_consumo.raise_for_status()
        data = r_consumo.json()
        guardar_json_crudo("datadis_consumo", data)

        df = pd.DataFrame(data)
        return guardar_csv(df, "datadis", f"consumo_{cups[-6:]}")

    except requests.exceptions.RequestException as e:
        print(f"  [ERROR DATADIS] {e}")
        return None


# ======================================================================
# MAIN
# ======================================================================

def main():
    print("=" * 70)
    print(" START ENERGY AI - Descarga de datos multi-fuente")
    print(f" Rango: {FECHA_INICIO} a {FECHA_FIN}")
    print("=" * 70)

    crear_carpetas()
    resultados = []

    # --- Activa / desactiva cada fuente aquí ---
    USAR_REE = True
    USAR_ESIOS = True
    USAR_AEMET = True
    USAR_PVGIS = True
    USAR_DATADIS = True

    if USAR_REE:
        resultados.append(descargar_ree("demanda", "demanda-tiempo-real", "demanda_horaria"))
        time.sleep(1)
        resultados.append(descargar_ree("generacion", "estructura-generacion", "generacion_estructura", time_trunc="day"))
        time.sleep(1)
        resultados.append(descargar_ree("generacion", "evolucion-renovable-no-renovable", "renovable_vs_no_renovable", time_trunc="day"))

    if USAR_ESIOS:
        resultados.append(descargar_esios_indicador(1293, "demanda_real"))
        time.sleep(1)
        resultados.append(descargar_esios_indicador(551, "generacion_eolica"))
        time.sleep(1)
        resultados.append(descargar_esios_indicador(549, "generacion_solar_fv"))

    if USAR_AEMET:
        resultados.append(descargar_aemet_climatologia())

    if USAR_PVGIS:
        resultados.append(descargar_pvgis_radiacion())
        resultados.append(descargar_pvgis_potencial_fv())

    if USAR_DATADIS:
        resultados.append(descargar_datadis_consumo())

    print("\n" + "=" * 70)
    exitosos = [r for r in resultados if r is not None]
    print(f" RESUMEN: {len(exitosos)}/{len(resultados)} descargas completadas correctamente")
    print(f" Archivos en: {CARPETA_DATOS.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()


# ======================================================================
# EJEMPLO DE ARCHIVO .env (opcional, en la misma carpeta que este script)
# ------------------------------------------------------------------------
# ESIOS_TOKEN=tu_token_de_consultasios
# AEMET_API_KEY=tu_api_key_de_aemet
# DATADIS_NIF=12345678A
# DATADIS_PASSWORD=tu_password
#
# Si usas .env, añade estas dos líneas al principio del script:
#   from dotenv import load_dotenv
#   load_dotenv()
# ======================================================================