import streamlit as st
import pandas as pd
import plotly.express as px # Para gráficos

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Admin Dashboard - Rifas", layout="wide")

# Inicializar datos si no existen
if 'ventas' not in st.session_state:
    st.session_state.ventas = pd.DataFrame(columns=["Ticket", "Cliente", "WhatsApp", "Punto_Venta", "Monto"])

# --- ESTILOS TIPO DASHBOARD ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
menu = st.sidebar.selectbox("Navegación", ["🛒 Ventas Público", "📊 Dashboard Admin"])

if menu == "📊 Dashboard Admin":
    st.title("🎛️ Panel de Control Administrativo")
    clave = st.sidebar.text_input("Clave de Acceso", type="password")

    if clave == "admin2025":
        # --- FILA 1: MÉTRICAS CLAVE ---
        col1, col2, col3 = st.columns(3)
        total_recaudado = st.session_state.ventas["Monto"].sum()
        tickets_vendidos = len(st.session_state.ventas)
        
        col1.metric("Total Recaudado", f"${total_recaudado}")
        col2.metric("Tickets Vendidos", f"{tickets_vendidos} / 100")
        col3.metric("Progreso", f"{(tickets_vendidos/100)*100}%")

        st.divider()

        # --- FILA 2: GRÁFICOS Y TABLAS ---
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("📈 Ventas por Punto de Venta")
            if not st.session_state.ventas.empty:
                fig = px.pie(st.session_state.ventas, names='Punto_Venta', values='Monto', hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Esperando datos de ventas...")

        with c2:
            st.subheader("📝 Registro Reciente")
            st.dataframe(st.session_state.ventas.tail(10), use_container_width=True)

        # --- FILA 3: CONFIGURACIÓN ---
        with st.expander("⚙️ Configuración del Sorteo"):
            nuevo_precio = st.number_input("Cambiar Precio Ticket", value=10.0)
            if st.button("Actualizar Parámetros"):
                st.success("Configuración guardada en el servidor.")
    else:
        st.error("Por favor, ingresa la clave de administrador para ver las métricas.")

else:
    st.title("🎟️ ¡Compra tu Ticket!")
    # Aquí iría el tablero de números que ya construimos anteriormente
    st.info("Selecciona un número del tablero para participar.")