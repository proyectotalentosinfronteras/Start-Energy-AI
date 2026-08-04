## Variables de Feature Engineering

- Variables temporales

hora

día_semana

mes

trimestre

fin_de_semana


- Variables retrasadas (Lag)

producción_1h

producción_2h

producción_24h

consumo_1h

consumo_24h


- Medias móviles

media_3h

media_6h

media_24h

-Variables derivadas

balance = producción - consumo

excedente

déficit

autoconsumo

ratio_autoconsumo

- Variables meteorológicas cruzadas

temperatura × radiación

nubosidad × radiación

humedad × temperatura




Variable objetivo

Nuestro modelo intentará predecir:

Producción Fotovoltaica (kWh)

Próximas

24 horas
Modelo recomendado
Baseline

Regresión Lineal

↓

Modelo principal

Random Forest Regressor

↓

Comparación

XGBoost

↓

Modelo avanzado

Prophet

Dashboard

Quiero que tenga estas páginas.

Página 1

Resumen

Producción hoy
Consumo hoy
Excedentes
Ahorro
Página 2

Producción

Gráfico

Real

vs

Predicha

Página 3

Consumo

Consumo

vs

Producción

Página 4

Alertas

Ejemplo

🟢

Entre las 13:00 y las 16:00 se prevé una generación superior al consumo. Se recomienda programar la carga del vehículo eléctrico o poner en marcha electrodomésticos de alto consumo.

Página 5

Meteorología

Radiación
Temperatura
Nubosidad






