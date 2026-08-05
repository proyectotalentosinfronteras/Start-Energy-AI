// dashboard/js/app.js - Lógica de Conexión de Start Energy AI
const API_DASHBOARD = "http://127.0.0";
let miGrafica = null; // Control de la instancia del gráfico

async function consultarServidor() {
    try {
        console.log("Conectando con el backend de Start Energy AI...");
        const respuesta = await fetch(API_DASHBOARD);
        if (!respuesta.ok) throw new Error(`Error en servidor: ${respuesta.status}`);
        
        const resultado = await respuesta.json();
        console.log("Datos recibidos:", resultado.data);
        
        // 1. Rellenar las tarjetas de texto de tu HTML original
        actualizarPantalla(resultado.data);
        
        // 2. Pintar la gráfica con las 3 curvas (Consumo, Solar e Inteligencia PVPC)
        dibujarGrafica(resultado.data);

    } catch (error) {
        console.error("Fallo de conexión con la API:", error);
    }
}

function actualizarPantalla(datosHorarios) {
    if (!datosHorarios || datosHorarios.length === 0) return;
    const estadoActual = datosHorarios[datosHorarios.length - 1];
    
    // Mapea los valores hacia los IDs que añadiste en tu HTML
    mapearTexto("consumo-actual", `${estadoActual.consumo_casa_datadis_kwh.toFixed(2)} kWh`);
    mapearTexto("generacion-actual", `${estadoActual.solar_esios_kwh.toFixed(2)} kWh`);
    mapearTexto("precio-actual", `${estadoActual.precio_pvpc_mwh ? estadoActual.precio_pvpc_mwh.toFixed(2) : '120.00'} €/MWh`);
    mapearTexto("temperatura-exterior", `${estadoActual.tmed ? estadoActual.tmed.toFixed(1) : '--'} °C`);
    
    // Algoritmo básico de optimización de excedentes en base a tu IA
    const balance = estadoActual.solar_esios_kwh - estadoActual.consumo_casa_datadis_kwh;
    const elementoConsejo = document.getElementById("recomendacion-ia");
    if (elementoConsejo) {
        if (balance > 0) {
            elementoConsejo.innerText = `💡 Excedente de ${balance.toFixed(2)} kWh detectado. ¡Momento óptimo para programar consumos!`;
            elementoConsejo.style.color = "#2ecc71"; // Cambia el texto a verde automáticamente
        } else {
            elementoConsejo.innerText = "📉 Consumo superior a la generación. Modera cargas o espera a horas con PVPC más económico.";
            elementoConsejo.style.color = "#e74c3c"; // Cambia el texto a rojo automáticamente
        }
    }
}

function dibujarGrafica(datosHorarios) {
    const ctx = document.getElementById('graficaEnergia');
    if (!ctx) return;

    // Convertimos la estampa de tiempo del CSV en horas legibles (Ej: "14:00")
    const etiquetasHoras = datosHorarios.map(d => {
        const fecha = new Date(d.datetime_clean);
        return `${fecha.getHours()}:00`;
    });

    const curvaConsumo = datosHorarios.map(d => d.consumo_casa_datadis_kwh);
    const curvaSolar = datosHorarios.map(d => d.solar_esios_kwh);
    const curvaPrecio = datosHorarios.map(d => d.precio_pvpc_mwh || 120.00);

    if (miGrafica) miGrafica.destroy(); // Limpia la gráfica vieja para evitar fallos de renderizado

    miGrafica = new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetasHoras,
            datasets: [
                {
                    label: 'Consumo (kWh)',
                    data: curvaConsumo,
                    borderColor: '#rose-500', // Sincronizado con estilos de Tailwind
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.05)',
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y' // Usa el eje izquierdo de potencia
                },
                {
                    label: 'Producción IA (kWh)',
                    data: curvaSolar,
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.05)',
                    tension: 0.3,
                    fill: true,
                    yAxisID: 'y' // Usa el eje izquierdo de potencia
                },
                {
                    label: 'Precio PVPC (€/MWh)',
                    data: curvaPrecio,
                    borderColor: '#f59e0b',
                    borderDash:, // Línea discontinua elegante
                    backgroundColor: 'transparent',
                    tension: 0.3,
                    yAxisID: 'y1' // Usa el eje derecho secundario para los costes
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Potencia / Energía (kWh)' },
                    beginAtZero: true
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Coste del Mercado (€/MWh)' },
                    grid: { drawOnChartArea: false }, // Evita que se crucen las líneas de cuadrícula
                    beginAtZero: false
                }
            }
        }
    });
}

function mapearTexto(idElemento, texto) {
    const el = document.getElementById(idElemento);
    if (el) el.innerText = texto;
}

// Escuchador de carga inicial
document.addEventListener("DOMContentLoaded", consultarServidor);

