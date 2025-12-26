import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Sistema de Rifas Profesional", layout="wide")

# --- PERSISTENCIA DE DATOS (Simulada, conectar a Google Sheets para producción) ---
if 'db_tickets' not in st.session_state:
    st.session_state.db_tickets = []
if 'puntos_venta' not in st.session_state:
    st.session_state.puntos_venta = pd.DataFrame([
        {"ID": "PV01", "Nombre": "Principal", "Clave": "123", "Capacidad": 1000, "Comision_V": 10, "Comision_P": 5, "Estado": "Activo"}
    ])
if 'sorteos' not in st.session_state:
    st.session_state.sorteos = ["Sorteo Mayor", "Rifa Rápida"]

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .ticket-box { border: 2px dashed #333; padding: 15px; border-radius: 10px; background: #fffce6; font-family: 'Courier New', Courier, monospace; }
    .metric-card { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #27ae60; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
with st.sidebar:
    st.title("🎟️ RIFAS CONTROL")
    rol = st.selectbox("Acceso", ["Punto de Venta", "Súper Administrador"])
    pwd = st.text_input("Contraseña", type="password")

# --- LÓGICA SÚPER ADMINISTRADOR ---
if rol == "Súper Administrador" and pwd == "MASTER2025":
    st.header("🛡️ Panel de Súper Administración")
    
    t1, t2, t3, t4 = st.tabs(["📍 Puntos de Venta", "🎰 Sorteos", "💸 Comisiones y Capacidad", "📊 Reporte Maestro"])

    with t1:
        st.subheader("Gestionar Vendedores")
        # Editor dinámico para añadir, modificar o eliminar
        new_pv = st.data_editor(st.session_state.puntos_venta, num_rows="dynamic", key="pv_editor")
        if st.button("Actualizar Puntos de Venta"):
            st.session_state.puntos_venta = new_pv
            st.success("Cambios reflejados en todos los puntos de venta.")

    with t2:
        st.subheader("Tipos de Sorteo")
        nuevo_s = st.text_input("Añadir nuevo sorteo")
        if st.button("Añadir Sorteo"):
            st.session_state.sorteos.append(nuevo_s)
            st.rerun()
        st.write("Sorteos actuales:", st.session_state.sorteos)

    with t3:
        st.subheader("Finanzas y Límites")
        st.info("Ajuste de porcentajes de comisión y capacidad de tickets.")
        st.write(st.session_state.puntos_venta[["Nombre", "Capacidad", "Comision_V", "Comision_P"]])

    with t4:
        st.subheader("Reporte Maestro de Utilidades")
        df_ventas = pd.DataFrame(st.session_state.db_tickets)
        if not df_ventas.empty:
            st.write("Balance General:")
            # Aquí irían cálculos de totales, premios pagados y ganancia neta
            st.dataframe(df_ventas)

# --- LÓGICA PUNTO DE VENTA ---
elif rol == "Punto de Venta":
    pv_info = st.session_state.puntos_venta[st.session_state.puntos_venta['Clave'] == pwd]
    
    if not pv_info.empty:
        vendedor = pv_info.iloc[0]
        if vendedor['Estado'] == "Activo":
            st.title(f"🏪 PV: {vendedor['Nombre']}")
            
            menu_v = st.tabs(["🎫 Vender Ticket", "📋 Reportes Diario/Mes", "⚠️ Caducados", "✅ Pagos"])
            
            with menu_v[0]:
                st.subheader("Generar Nueva Venta")
                col_a, col_b = st.columns(2)
                with col_a:
                    num_escogido = st.number_input("Número", 0, 9999)
                    sorteo = st.selectbox("Sorteo", st.session_state.sorteos)
                with col_b:
                    valor = st.number_input("Valor Compra $", 1.0)
                    premio_estimado = valor * 50 # Ejemplo de suerte
                
                if st.button("🎰 Generar e Imprimir Ticket"):
                    # Crear Datos del Ticket
                    id_unico = str(uuid.uuid4())[:8].upper()
                    serie = f"SER-{random.randint(1000,9999)}"
                    fecha_c = datetime.now()
                    vencimiento = fecha_c + timedelta(days=7)
                    
                    nuevo_ticket = {
                        "ID": id_unico, "Serie": serie, "Vendedor": vendedor['Nombre'],
                        "Numero": num_escogido, "Valor": valor, "Premio": premio_estimado,
                        "Fecha": fecha_c, "Vence": vencimiento, "Estado": "Pendiente",
                        "Ganador": "No"
                    }
                    st.session_state.db_tickets.append(nuevo_ticket)
                    
                    # DISEÑO DEL TICKET PARA EL CLIENTE
                    st.markdown(f"""
                    <div class="ticket-box">
                        <h3 style='text-align:center;'>TICKET DE RIFA</h3>
                        <p><b>Serie:</b> {serie} | <b>ID:</b> {id_unico}</p>
                        <p><b>Vendedor:</b> {vendedor['Nombre']}</p>
                        <hr>
                        <h2 style='text-align:center;'>NÚMERO: {num_escogido}</h2>
                        <p><b>Premio Potencial:</b> ${premio_estimado}</p>
                        <p><b>Fecha:</b> {fecha_c.strftime('%d/%m/%Y %H:%M')}</p>
                        <p><b>Caduca:</b> {vencimiento.strftime('%d/%m/%Y')}</p>
                    </div>
                    """, unsafe_allow_html=True)

            with menu_v[1]:
                st.subheader("Reporte de Ventas")
                df_v = pd.DataFrame(st.session_state.db_tickets)
                if not df_v.empty:
                    df_v_vendedor = df_v[df_v['Vendedor'] == vendedor['Nombre']]
                    st.write("Resumen Mensual:")
                    st.dataframe(df_v_vendedor)

            with menu_v[2]:
                st.subheader("Tickets Caducados (Periodo 7 días)")
                ahora = datetime.now()
                df_c = pd.DataFrame(st.session_state.db_tickets)
                if not df_c.empty:
                    caducados = df_c[df_c['Vence'] < ahora]
                    st.warning(f"Se han encontrado {len(caducados)} tickets fuera de fecha.")
                    st.table(caducados[["Serie", "Numero", "Vence"]])

            with menu_v[3]:
                st.subheader("Validar y Pagar Ticket")
                code_scan = st.text_input("Ingrese Código Único del Ticket")
                if st.button("Marcar como PAGADO"):
                    for t in st.session_state.db_tickets:
                        if t['ID'] == code_scan:
                            t['Estado'] = "Pagado"
                            st.success(f"Ticket {t['Serie']} actualizado a PAGADO.")

        else:
            st.error("Punto de Venta BLOQUEADO. Contacte al administrador.")
    else:
        st.info("Esperando clave de vendedor...")