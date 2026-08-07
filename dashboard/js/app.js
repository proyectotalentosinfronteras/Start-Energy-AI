// dashboard/js/app.js - Lógica de Conexión de Start Energy AI
const API_DASHBOARD = "http://127.0.0.1:8000";
let miGrafica = null; // Control de la instancia del gráfico

async function consultarServidor() {
    try {
        console.log("Conectando con el backend de Start Energy AI...");
        const respuesta = await fetch(`${API_DASHBOARD}/api/v1/dashboard-data`);
        if (!respuesta.ok) throw new Error(`Error en servidor: ${respuesta.status}`);
        
        const resultado = await respuesta.json();
        console.log("Datos recibidos:", resultado);
        
        // 1. Rellenar las tarjetas de texto y KPIs
        actualizarPantalla(resultado);
        
        // 2. Pintar la gráfica con el histórico y predicciones unificadas
        dibujarGrafica(resultado.historico);

    } catch (error) {
        console.error("Fallo de conexión con la API:", error);
    }
}

function actualizarPantalla(data) {
    if (!data) return;
    
    // Mapeo utilizando la estructura JSON unificada que definimos
    mapearTexto("consumo-actual", `${data.actual.consumo} kWh`);
    mapearTexto("generacion-actual", `${data.actual.generacion_solar} kWh`);
    mapearTexto("precio-actual", `${data.actual.precio_energia} €/kWh`);
    mapearTexto("temperatura-exterior", `${data.actual.temperatura} °C`);
    
    const elementoConsejo = document.getElementById("recomendacion-ia");
    if (elementoConsejo && data.alertas && data.alertas.length > 0) {
        elementoConsejo.innerText = `💡 ${data.alertas[0].mensaje}`;
        elementoConsejo.style.color = "#2ecc71";
    }
}

function dibujarGrafica(historico) {
    const ctx = document.getElementById('graficaEnergia');
    if (!ctx || !historico) return;

    if (miGrafica) miGrafica.destroy();

    miGrafica = new Chart(ctx, {
        type: 'line',
        data: {
            labels: historico.fechas,
            datasets: [
                {
                    label: 'Consumo (kWh)',
                    data: historico.consumo,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.05)',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Producción Solar (kWh)',
                    data: historico.generacion_solar,
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.05)',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function mapearTexto(idElemento, texto) {
    const el = document.getElementById(idElemento);
    if (el) el.innerText = texto;
}

// Escuchador de carga inicial
document.addEventListener("DOMContentLoaded", consultarServidor);