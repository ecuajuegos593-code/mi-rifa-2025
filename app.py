import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE SEGURIDAD Y ESTADO ---
if 'puntos_venta' not in st.session_state:
    # Base de datos inicial de vendedores
    st.session_state.puntos_venta = pd.DataFrame([
        {"id": "001", "nombre": "Sede Central", "clave": "123", "estado": "Activo"},
        {"id": "002", "nombre": "Vendedor Norte", "clave": "456", "estado": "Activo"}
    ])

if 'config_global' not in st.session_state:
    st.session_state.config_global = {
        "nombre_rifa": "Gran Sorteo 2025",
        "precio_ticket": 10.0,
        "total_tickets": 100,
        "estado_sorteo": "Abierto"
    }

# --- INTERFAZ ---
st.sidebar.title("🔐 Acceso al Sistema")
acceso = st.sidebar.selectbox("Tipo de Usuario", ["Punto de Venta", "Súper Administrador"])
password_input = st.sidebar.text_input("Contraseña", type="password")

# --- LÓGICA DE SÚPER ADMINISTRADOR ---
if acceso == "Súper Administrador" and password_input == "MASTER2025":
    st.title("🛡️ Panel de Súper Administración")
    
    tab1, tab2, tab3 = st.tabs(["📍 Puntos de Venta", "⚙️ Parámetros Globales", "📊 Auditoría"])

    with tab1:
        st.subheader("Gestión de Puntos de Venta")
        
        # Formulario para añadir nuevo vendedor
        with st.expander("➕ Añadir Nuevo Punto de Venta"):
            new_id = st.text_input("ID único")
            new_name = st.text_input("Nombre del Punto/Vendedor")
            new_pass = st.text_input("Clave de acceso para este punto")
            if st.button("Registrar Vendedor"):
                new_row = {"id": new_id, "nombre": new_name, "clave": new_pass, "estado": "Activo"}
                st.session_state.puntos_venta = pd.concat([st.session_state.puntos_venta, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Vendedor añadido con éxito")

        # Tabla de gestión (Eliminar o Bloquear)
        st.write("### Vendedores Actuales")
        edited_df = st.data_editor(st.session_state.puntos_venta, num_rows="dynamic", key="editor_vendedores")
        if st.button("Guardar Cambios en Vendedores"):
            st.session_state.puntos_venta = edited_df
            st.success("Base de datos de vendedores actualizada")

    with tab2:
        st.subheader("Configuración del Sorteo")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.config_global['nombre_rifa'] = st.text_input("Nombre del Evento", st.session_state.config_global['nombre_rifa'])
            st.session_state.config_global['precio_ticket'] = st.number_input("Precio ($)", value=st.session_state.config_global['precio_ticket'])
        with col2:
            st.session_state.config_global['estado_sorteo'] = st.selectbox("Estado del Sorteo", ["Abierto", "Pausado", "Finalizado"])
            st.session_state.config_global['total_tickets'] = st.number_input("Cantidad de Números", value=st.session_state.config_global['total_tickets'])

    with tab3:
        st.subheader("Reporte General de Ingresos")
        st.info("Aquí verás la suma de todos los puntos de venta consolidados.")

# --- LÓGICA DE PUNTO DE VENTA (VENDEDOR) ---
elif acceso == "Punto de Venta":
    # Verificar si el vendedor existe y su clave es correcta
    vendedor_info = st.session_state.puntos_venta[st.session_state.puntos_venta['clave'] == password_input]
    
    if not vendedor_info.empty:
        vendedor_actual = vendedor_info.iloc[0]
        if vendedor_actual['estado'] == "Activo":
            st.title(f"🏪 Punto de Venta: {vendedor_actual['nombre']}")
            st.write(f"Vendiendo para: **{st.session_state.config_global['nombre_rifa']}**")
            
            # Aquí va el código de los botones del 1 al 100 para vender
            st.success("Acceso autorizado para ventas.")
        else:
            st.error("Este punto de venta se encuentra BLOQUEADO.")
    else:
        st.warning("Ingrese su clave de vendedor para continuar.")