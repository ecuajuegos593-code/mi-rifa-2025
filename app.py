import streamlit as st
import pandas as pd
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rifa Master Pro", page_icon="🎟️", layout="wide")

# --- INICIALIZACIÓN DE DATOS (Simulando Base de Datos) ---
if 'db_tickets' not in st.session_state:
    st.session_state.db_tickets = {i: {"estado": "Disponible", "cliente": "", "tel": ""} for i in range(1, 101)}
if 'puntos_venta' not in st.session_state:
    st.session_state.puntos_venta = ["Sede Central", "Web"]

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .vendido { background-color: #ff4b4b !important; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN LATERAL ---
st.sidebar.title("🎟️ Menú Principal")
modo = st.sidebar.radio("Navegar a:", ["🛒 Venta de Tickets", "🔐 Administración"])

# --- SECCIÓN DE ADMINISTRACIÓN ---
if modo == "🔐 Administración":
    st.header("Panel Administrativo")
    password = st.sidebar.text_input("Clave de Acceso", type="password")
    
    if password == "admin2025": # <--- Cambia tu clave aquí
        tab1, tab2, tab3 = st.tabs(["📈 Reportes", "📍 Puntos de Venta", "⚙️ Configuración"])
        
        with tab1:
            st.subheader("Ventas Realizadas")
            df = pd.DataFrame.from_dict(st.session_state.db_tickets, orient='index')
            ventas_reales = df[df['estado'] == 'Vendido']
            
            if not ventas_reales.empty:
                st.dataframe(ventas_reales)
                
                # --- BOTÓN PARA DESCARGAR EXCEL ---
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    ventas_reales.to_excel(writer, sheet_name='Ganadores')
                
                st.download_button(
                    label="📥 Descargar Reporte Excel",
                    data=buffer.getvalue(),
                    file_name="reporte_rifa.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.info("Aún no hay ventas registradas.")

        with tab2:
            st.subheader("Gestión de Puntos de Venta")
            nuevo_punto = st.text_input("Nombre del nuevo punto")
            if st.button("Añadir Punto"):
                st.session_state.puntos_venta.append(nuevo_punto)
                st.success(f"Punto '{nuevo_punto}' añadido.")
            st.write("Puntos actuales:", st.session_state.puntos_venta)

    else:
        st.error("Clave incorrecta para acceder al panel.")

# --- SECCIÓN DE VENTAS ---
else:
    st.header("🛒 Venta de Tickets")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("### Selecciona tus números")
        # Generar cuadrícula de 10 columnas
        cols = st.columns(10)
        for i in range(1, 101):
            with cols[(i-1) % 10]:
                estado = st.session_state.db_tickets[i]["estado"]
                if estado == "Disponible":
                    if st.button(f"{i}", key=f"btn_{i}"):
                        st.session_state.seleccionado = i
                else:
                    st.button(f"{i}", key=f"btn_{i}", disabled=True, help="Vendido")

    with col2:
        st.write("### Detalle de Compra")
        if 'seleccionado' in st.session_state:
            num = st.session_state.seleccionado
            st.success(f"Número seleccionado: **{num}**")
            nombre = st.text_input("Nombre Completo")
            telefono = st.text_input("Teléfono / WhatsApp")
            punto = st.selectbox("Punto de Venta", st.session_state.puntos_venta)
            
            if st.button("Confirmar y Registrar"):
                if nombre and telefono:
                    st.session_state.db_tickets[num] = {
                        "estado": "Vendido",
                        "cliente": nombre,
                        "tel": telefono,
                        "punto": punto
                    }
                    st.balloons()
                    st.success(f"¡Ticket {num} registrado!")
                    del st.session_state.seleccionado
                    st.rerun()
                else:
                    st.warning("Por favor llena los datos del cliente.")
        else:
            st.info("Haz clic en un número del tablero para iniciar la venta.")