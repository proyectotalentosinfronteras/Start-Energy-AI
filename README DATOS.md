# Start Energy AI — Descarga de datos multi-fuente

Script de descarga automática para el proyecto final. Descarga datos reales de:

| Fuente | Datos | Token necesario |
|---|---|---|
| REE / REData | Demanda y generación horaria | No |
| ESIOS (REE) | Indicadores detallados (demanda, eólica, solar, precio) | Sí — email a `consultasios@ree.es` |
| AEMET OpenData | Climatología diaria / radiación | Sí — desde `opendata.aemet.es` |
| PVGIS (UE) | Radiación solar horaria y producción FV estimada | No |
| Datadis | Consumo eléctrico horario por CUPS | Usuario/NIF + contraseña de tu cuenta en `datadis.es` |

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Abre `descarga_datos.py` y edita la sección **CONFIGURACIÓN** al principio del archivo:

- `FECHA_INICIO` / `FECHA_FIN`: rango de fechas a descargar
- `LATITUD` / `LONGITUD`: coordenadas para PVGIS
- `ESIOS_TOKEN`, `AEMET_API_KEY`, `DATADIS_NIF`, `DATADIS_PASSWORD`: tus credenciales

**Alternativa más segura:** en lugar de escribir las credenciales directamente en el
script, crea un archivo `.env` en la misma carpeta:

```
ESIOS_TOKEN=tu_token
AEMET_API_KEY=tu_api_key
DATADIS_NIF=12345678A
DATADIS_PASSWORD=tu_password
```

y descomenta las dos líneas de `load_dotenv()` al final del script.

## Ejecución

```bash
python descarga_datos.py
```

Puedes desactivar cualquier fuente cambiando su flag (`USAR_REE`, `USAR_ESIOS`, etc.)
a `False` dentro de la función `main()` — útil mientras esperas algún token.

## Resultado

```
data/
├── ree/
│   ├── demanda_horaria.csv
│   ├── generacion_estructura.csv
│   └── renovable_vs_no_renovable.csv
├── esios/
│   ├── demanda_real.csv
│   ├── generacion_eolica.csv
│   └── generacion_solar_fv.csv
├── aemet/
│   └── climatologia_diaria.csv
├── pvgis/
│   ├── radiacion_horaria.csv
│   └── produccion_fv_mensual.csv
├── datadis/
│   └── consumo_XXXXXX.csv
└── raw_json/          <- respaldo de cada respuesta cruda, por si necesitas auditar
```

Todos los CSV están en UTF-8, con la columna de fecha ya convertida a `datetime`
(cuando aplica), listos para cargar directamente en pandas o Power BI.

## Notas importantes

- **AEMET**: la estación por defecto es `8025` (Alicante/Elche). Cámbiala si tu
  proyecto necesita otra ubicación — puedes buscar el código en el catálogo de
  estaciones de AEMET OpenData.
- **PVGIS**: la API suele ir 1-2 años por detrás del año en curso; si pides un año
  muy reciente y no hay datos, prueba con el año anterior.
- **Datadis**: la API solo devuelve consumo de los CUPS asociados a la cuenta con
  la que te autentiques. Si necesitas datos de un tercero, hace falta autorización
  previa dentro de la plataforma.
- Cada fuente se descarga de forma independiente — si una falla (token mal puesto,
  fecha sin datos, etc.) el script sigue con las demás y te avisa al final cuántas
  se completaron.
