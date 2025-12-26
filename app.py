import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard de Rifas", layout="wide")

# --- CSS PARA IMITAR EL DISEÑO DEL CÓDIGO FUENTE (Cards de Colores) ---
st.markdown("""
<style>
    .card-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .card {
        flex: 1;
        padding: 20px;
        border-radius: 8px;
        color: white;
        text-align: left;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .bg-success { background-color: #27ae60; } /* Ventas Hoy */
    .bg-info { background-color: #2980b9; }    /* Ganadores Pendientes */
    .bg-primary { background-color: #3f51b5; } /* Ganadores Cobrados */
    .bg-danger { background-color: #e74c3c; }  /* No Cobrados */
    .card-title { font-size: 0.9em; text-transform: uppercase; opacity: 0.9; }
    .card-value { font-size: 1.8em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SIMULACIÓN DE DATOS (Adaptado de tu código fuente) ---
if 'db_ventas' not in st.session_state:
    # Datos de ejemplo basados en las categorías del dashboard
    st.session_state.db_ventas = {
        "ventas_hoy": 0.00,
        "ganadores_pendientes": 0.00,
        "ganadores_pagados": 0.00,
        "ganadores_no_cobrados": 0.00
    }

# --- BARRA LATERAL (Navegación del código fuente) ---
with st.sidebar:
    st.image("http://52.201.2.30/apt3/assets/img/logo3.png", width=150)
    st.title("Menú Sistema")
    opcion = st.radio("Navegar", ["📊 Reportes (Dashboard)", "🛒 Vender", "🔍 Caducados", "⚙️ Admin Reportes"])
    st.divider()
    if st.button("🚪 Finalizar Sesión"):
        st.write("Sesión cerrada")

# --- LÓGICA DE LAS SECCIONES ---

if opcion == "📊 Reportes (Dashboard)":
    st.header("Dashboard de Control")
    
    # Renderizar las Cards estilo "view-source"
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''<div class="card bg-success">
            <div class="card-title">Ventas Hoy</div>
            <div class="card-value">${st.session_state.db_ventas["ventas_hoy"]:.2f}</div>
        </div>''', unsafe_allow_html=True)
        
    with col2:
        st.markdown(f'''<div class="card bg-info">
            <div class="card-title">Ganadores Pendientes</div>
            <div class="card-value">${st.session_state.db_ventas["ganadores_pendientes"]:.2f}</div>
        </div>''', unsafe_allow_html=True)
        
    with col3:
        st.markdown(f'''<div class="card bg-primary">
            <div class="card-title">Ganadores Pagados</div>
            <div class="card-value">${st.session_state.db_ventas["ganadores_pagados"]:.2f}</div>
        </div>''', unsafe_allow_html=True)
        
    with col4:
        st.markdown(f'''<div class="card bg-danger">
            <div class="card-title">No Cobrados (8-15 días)</div>
            <div class="card-value">${st.session_state.db_ventas["ganadores_no_cobrados"]:.2f}</div>
        </div>''', unsafe_allow_html=True)

    st.divider()
    st.subheader("Ventas Recientes")
    # Aquí puedes añadir la tabla de los últimos movimientos
    st.info("No hay movimientos registrados en las últimas 24 horas.")

elif opcion == "🛒 Vender":
    st.header("Módulo de Ventas")
    # Aquí reutilizamos el código de los botones de números (1-100) que hicimos antes
    st.write("Seleccione el ticket a vender:")
    ticket_num = st.number_input("Número de Ticket", 1, 100)
    if st.button("Confirmar Venta"):
        st.success(f"Venta del ticket {ticket_num} procesada con éxito.")