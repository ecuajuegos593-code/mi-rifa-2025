import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="SISTEMA MASTER RIFA", layout="wide", page_icon="🎟️")

# --- 2. PERSISTENCIA Y ESTADO (Base de Datos en Memoria) ---
# Nota: Para persistencia permanente, conectar con Google Sheets
if 'db_tickets' not in st.session_state:
    st.session_state.db_tickets = []
if 'puntos_venta' not in st.session_state:
    st.session_state.puntos_venta = pd.DataFrame([
        {"ID": "001", "Nombre": "Oficina Central", "Clave": "MASTER2025", "Capacidad": 5000, "Comision_V": 10.0, "Comision_P": 5.0, "Estado": "Activo"}
    ])
if 'sorteos' not in st.session_state:
    st.session_state.sorteos = ["Sorteo Diario", "Sorteo Semanal"]

# --- 3. ESTILOS VISUALES (CSS) ---
st.markdown("""
    <style>
    .report-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #0e1117; }
    .ticket-box { border: 2px dashed #000; padding: 20px; background-color: #fff; color: #000; font-family: monospace; line-height: 1.2; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL (CONTROL DE ACCESO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("🔐 Acceso")
    rol = st.selectbox("Perfil:", ["Punto de Venta", "Súper Administrador"])
    password_input = st.text_input("Contraseña de acceso:", type="password")
    st.divider()
    st.caption("v2.0 - Sistema Independiente")

# --- 5. LÓGICA DE SÚPER ADMINISTRADOR ---
if rol == "Súper Administrador" and password_input == "MASTER2025":
    st.title("🛡️ Panel Global de Súper Administrador")
    
    t_admin = st.tabs(["📍 Puntos de Venta", "🎰 Config. Sorteos", "📊 Reporte Maestro"])

    with t_admin[0]:
        st.subheader("Administrar Vendedores y Sucursales")
        st.info("Aquí puedes añadir, bloquear o eliminar puntos de venta. Los cambios se reflejan al instante.")
        # Editor de tabla dinámico
        updated_pv = st.data_editor(st.session_state.puntos_venta, num_rows="dynamic", key="admin_pv_editor")
        if st.button("💾 Guardar Cambios en Puntos de Venta"):
            st.session_state.puntos_venta = updated_pv
            st.success("Base de datos de vendedores actualizada.")

    with t_admin[1]:
        st.subheader("Configuración de Sorteos y Capacidad")
        col1, col2 = st.columns(2)
        with col1:
            nuevo_sorteo = st.text_input("Nombre de nuevo tipo de sorteo:")
            if st.button("➕ Añadir Sorteo"):
                if nuevo_sorteo:
                    st.session_state.sorteos.append(nuevo_sorteo)
                    st.rerun()
        with col2:
            st.write("Sorteos Activos:")
            for s in st.session_state.sorteos:
                st.code(s)

    with t_admin[2]:
        st.subheader("Dashboard Financiero Consolidado")
        if st.session_state.db_tickets:
            df_m = pd.DataFrame(st.session_state.db_tickets)
            total_v = df_m['Valor'].sum()
            total_p = df_m[df_m['Estado'] == 'Pagado']['Valor'].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ventas Totales", f"${total_v:,.2f}")
            c2.metric("Premios Pagados", f"${total_p:,.2f}")
            c3.metric("Tickets Activos", len(df_m))
            st.dataframe(df_m)
        else:
            st.info("No hay ventas registradas aún.")

# --- 6. LÓGICA DE PUNTO DE VENTA ---
elif rol == "Punto de Venta":
    # Buscar vendedor por contraseña
    vendedor_match = st.session_state.puntos_venta[st.session_state.puntos_venta['Clave'] == password_input]
    
    if not vendedor_match.empty:
        v_data = vendedor_match.iloc[0]
        if v_data['Estado'] == "Activo":
            st.title(f"🏪 Punto de Venta: {v_data['Nombre']}")
            
            t_pv = st.tabs(["🎫 Vender", "📈 Mis Reportes", "⌛ Caducados", "✅ Cobros"])

            with t_pv[0]:
                st.subheader("Generar Nuevo Ticket")
                c_v1, c_v2 = st.columns(2)
                with c_v1:
                    n_ticket = st.number_input("Número de Suerte", 0, 99999, step=1)
                    s_tipo = st.selectbox("Seleccione Sorteo", st.session_state.sorteos)
                with c_v2:
                    v_ticket = st.number_input("Valor de Compra ($)", 1.0, 1000.0, step=0.5)
                    premio_p = v_ticket * 50 # Ejemplo de cálculo de premio
                
                if st.button("🚀 Emitir Ticket"):
                    # Generación de datos únicos
                    id_ticket = str(uuid.uuid4())[:8].upper()
                    n_serie = f"SN-{random.randint(10000, 99999)}"
                    f_ahora = datetime.now()
                    f_vence = f_ahora + timedelta(days=7)
                    
                    ticket_info = {
                        "ID": id_ticket, "Serie": n_serie, "Vendedor": v_data['Nombre'],
                        "Numero": n_ticket, "Valor": v_ticket, "Premio": premio_p,
                        "Fecha": f_ahora, "Vence": f_vence, "Estado": "Pendiente", "Sorteo": s_tipo
                    }
                    st.session_state.db_tickets.append(ticket_info)
                    
                    # REPRESENTACIÓN VISUAL DEL TICKET
                    st.markdown(f"""
                    <div class="ticket-box">
                        <h2 style="text-align:center;">{v_data['Nombre']}</h2>
                        <p style="text-align:center;">Ticket de Participación</p>
                        <hr>
                        <p><b>SORTEO:</b> {s_tipo}</p>
                        <p><b>SERIE:</b> {n_serie} | <b>ID:</b> {id_ticket}</p>
                        <h1 style="text-align:center; margin:10px 0;"># {n_ticket}</h1>
                        <p><b>VALOR:</b> ${v_ticket:,.2f} | <b>PREMIO:</b> ${premio_p:,.2f}</p>
                        <p><b>FECHA:</b> {f_ahora.strftime('%d/%m/%Y %H:%M')}</p>
                        <p style="color:red;"><b>VENCE:</b> {f_vence.strftime('%d/%m/%Y')}</p>
                        <p style="font-size:10px; text-align:center;">Conserve este ticket para cobrar su premio.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()

            with t_pv[1]:
                st.subheader("Reporte de Ventas (Diario / Mes)")
                if st.session_state.db_tickets:
                    df_v = pd.DataFrame(st.session_state.db_tickets)
                    df_v_vendedor = df_v[df_v['Vendedor'] == v_data['Nombre']]
                    st.dataframe(df_v_vendedor)
                else:
                    st.info("Aún no tienes ventas registradas.")

            with t_pv[2]:
                st.subheader("Reporte de Tickets Caducados")
                st.info("Los tickets caducan automáticamente a los 7 días de la compra.")
                if st.session_state.db_tickets:
                    df_c = pd.DataFrame(st.session_state.db_tickets)
                    caducados = df_c[(df_c['Vence'] < datetime.now()) & (df_c['Vendedor'] == v_data['Nombre'])]
                    st.table(caducados[["Serie", "Numero", "Vence", "Estado"]])

            with t_pv[3]:
                st.subheader("Módulo de Cobro y Validación")
                id_search = st.text_input("Ingrese Código Único (ID) del Ticket:")
                if st.button("🔍 Validar y Marcar como PAGADO"):
                    encontrado = False
                    for t in st.session_state.db_tickets:
                        if t['ID'] == id_search:
                            t['Estado'] = "Pagado"
                            st.success(f"Ticket {t['Serie']} marcado como PAGADO exitosamente.")
                            encontrado = True
                    if not encontrado:
                        st.error("Código no encontrado o inválido.")

        else:
            st.error("⚠️ Acceso denegado: Este Punto de Venta ha sido BLOQUEADO por el Administrador.")
    else:
        st.warning("Por favor, ingrese una clave de vendedor válida.")

else:
    st.info("👋 Bienvenid@. Seleccione su perfil y use su clave para ingresar.")