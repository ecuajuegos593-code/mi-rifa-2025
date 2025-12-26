import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. CONFIGURACIÓN VISUAL Y COLORES ---
st.set_page_config(page_title="Rifa Profesional", page_icon="💰", layout="wide")

# Estilo personalizado con CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        border-radius: 10px; 
        height: 3em; 
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { border: 2px solid #007bff; color: #007bff; }
    h1 { color: #1e3a8a; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DATOS EN MEMORIA ---
if 'db_tickets' not in st.session_state:
    st.session_state.db_tickets = {i: {"estado": "Disponible", "cliente": "", "tel": ""} for i in range(1, 101)}
if 'config' not in st.session_state:
    st.session_state.config = {
        "premio": "Gran Premio Sorpresa",
        "precio": 5.0,
        "organizador": "Mi Rifa Online",
        "imagen_url": "https://via.placeholder.com/600x200.png?text=Imagen+del+Premio+Aqui"
    }

# --- 3. BARRA LATERAL (NAVEGACIÓN) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Panel de Control")
    modo = st.radio("Sección:", ["🏠 Inicio / Compra", "🛠️ Ajustes del Sorteo", "📊 Ver Ventas"])
    st.divider()
    password = st.text_input("Clave Admin", type="password")

# --- SECCIÓN: AJUSTES DEL SORTEO (MODIFICACIONES) ---
if modo == "🛠️ Ajustes del Sorteo":
    if password == "admin2025":
        st.header("Modificar Datos del Sorteo")
        st.session_state.config['premio'] = st.text_input("Nombre del Premio", st.session_state.config['premio'])
        st.session_state.config['precio'] = st.number_input("Precio por Ticket", value=st.session_state.config['precio'])
        st.session_state.config['imagen_url'] = st.text_input("URL de Imagen del Premio (Link)", st.session_state.config['imagen_url'])
        st.success("Configuración actualizada.")
    else:
        st.warning("Ingresa la clave correcta para modificar.")

# --- SECCIÓN: INICIO / COMPRA ---
elif modo == "🏠 Inicio / Compra":
    st.title(f"🎟️ {st.session_state.config['organizador']}")
    
    # Mostrar imagen del premio
    st.image(st.session_state.config['imagen_url'], use_container_width=True)
    
    st.subheader(f"Sorteo de: {st.session_state.config['premio']}")
    st.info(f"💰 Valor: ${st.session_state.config['precio']} por número")

    # Grid de números
    cols = st.columns(10)
    for i in range(1, 101):
        with cols[(i-1) % 10]:
            estado = st.session_state.db_tickets[i]["estado"]
            color = "primary" if estado == "Disponible" else "secondary"
            if st.button(f"{i}", key=f"t{i}", type=color, disabled=(estado != "Disponible")):
                st.session_state.selected = i

    # Formulario de compra flotante
    if 'selected' in st.session_state:
        with st.expander(f"🛒 COMPRAR NÚMERO {st.session_state.selected}", expanded=True):
            nombre = st.text_input("Tu Nombre")
            tel = st.text_input("WhatsApp")
            if st.button("Finalizar Compra"):
                if nombre and tel:
                    st.session_state.db_tickets[st.session_state.selected] = {
                        "estado": "Vendido", "cliente": nombre, "tel": tel
                    }
                    st.success(f"¡Número {st.session_state.selected} reservado!")
                    del st.session_state.selected
                    st.balloons()
                    st.rerun()

# --- SECCIÓN: VER VENTAS ---
elif modo == "📊 Ver Ventas":
    if password == "admin2025":
        st.header("Reporte de Ventas")
        df = pd.DataFrame.from_dict(st.session_state.db_tickets, orient='index')
        ventas = df[df['estado'] == 'Vendido']
        
        if not ventas.empty:
            st.dataframe(ventas)
            # Descargar Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                ventas.to_excel(writer, sheet_name='Ventas')
            st.download_button("Descargar Excel", output.getvalue(), "ventas.xlsx")
        else:
            st.write("No hay ventas todavía.")
    else:
        st.error("Acceso denegado.")