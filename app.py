import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Rifas Profesional", layout="wide", page_icon="🎟️")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS (Sesión Local) ---
if 'db_ventas' not in st.session_state:
    st.session_state.db_ventas = pd.DataFrame(columns=[
        'id_serie', 'codigo_pago', 'numero', 'vendedor', 'monto', 'fecha', 'hora', 'estado'
    ])

if 'puntos_venta' not in st.session_state:
    st.session_state.puntos_venta = pd.DataFrame([
        {'usuario': 'admin', 'clave': '1234', 'rol': 'Super Admin', 'estado': 'Activo'},
        {'usuario': 'vendedor1', 'clave': 'vende01', 'rol': 'Punto de Venta', 'estado': 'Activo'}
    ])

# --- SISTEMA DE LOGIN ---
if 'user' not in st.session_state:
    st.title("🔐 Acceso al Sistema de Rifas")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            match = st.session_state.puntos_venta[
                (st.session_state.puntos_venta['usuario'] == u) & 
                (st.session_state.puntos_venta['clave'] == p) &
                (st.session_state.puntos_venta['estado'] == 'Activo')
            ]
            if not match.empty:
                st.session_state.user = u
                st.session_state.rol = match.iloc[0]['rol']
                st.rerun()
            else:
                st.error("Error: Usuario o clave incorrectos.")
    st.stop()

# --- BARRA LATERAL (MENÚ) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3408/3408506.png", width=80)
    st.write(f"👤 **{st.session_state.user}**")
    st.write(f"🎖️ {st.session_state.rol}")
    st.divider()
    
    opciones = ["Inicio", "Vender Tickets", "Mis Reportes"]
    if st.session_state.rol == "Super Admin":
        opciones += ["--- ADMIN ---", "Gestionar Vendedores", "Configurar Sorteo", "Finanzas Globales", "Ganadores"]
    
    choice = st.radio("Menu", opciones)
    
    if st.button("Cerrar Sesión"):
        del st.session_state.user
        st.rerun()

# --- LÓGICA DE LAS SECCIONES ---

if choice == "Inicio":
    st.title("🏠 Panel de Control")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.info("### Sorteo Activo: Gran Rifa 2024\nFecha: 31 de Diciembre")
    with col_i2:
        st.success(f"### Tickets Vendidos Hoy\n{len(st.session_state.db_ventas[st.session_state.db_ventas['fecha'] == datetime.now().strftime('%Y-%m-%d')])}")

elif choice == "Vender Tickets":
    st.header("🎟️ Venta de Tickets")
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        num = st.number_input("Número (00-99)", 0, 99, format="%02d")
        monto = st.selectbox("Monto $", [1.0, 2.0, 5.0, 10.0])
        
        if st.button("✅ Confirmar Venta"):
            serie = str(uuid.uuid4())[:8].upper()
            codigo = f"PY-{random.randint(100, 999)}-{random.randint(10, 99)}"
            nueva_venta = {
                'id_serie': serie, 'codigo_pago': codigo, 'numero': f"{num:02d}",
                'vendedor': st.session_state.user, 'monto': monto,
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'hora': datetime.now().strftime("%H:%M:%S"), 'estado': 'Activo'
            }
            st.session_state.db_ventas = pd.concat([st.session_state.db_ventas, pd.DataFrame([nueva_venta])], ignore_index=True)
            st.session_state.ultimo_ticket = nueva_venta
            st.success("Ticket generado correctamente.")

    with c2:
        if 'ultimo_ticket' in st.session_state:
            t = st.session_state.ultimo_ticket
            # --- DISEÑO DEL TICKET HTML ---
            ticket_html = f"""
            <div id="ticket-area" style="width: 75mm; padding: 10px; background: white; color: black; border: 1px solid #000; font-family: 'Courier New', monospace;">
                <center>
                    <h2 style="margin:0;">LOTERÍA PRO</h2>
                    <p style="font-size: 10px; margin:0;">RIFA DEL SORTEO MAYOR</p>
                    <hr style="border-top: 1px dashed #000;">
                    <span style="font-size: 14px;">NÚMERO ELEGIDO</span><br>
                    <span style="font-size: 45px; font-weight: bold;">{t['numero']}</span><br>
                    <span style="font-size: 18px;">VALOR: ${t['monto']}</span>
                    <hr style="border-top: 1px dashed #000;">
                    <div style="text-align: left; font-size: 11px;">
                        FECHA: {t['fecha']} {t['hora']}<br>
                        SERIE: {t['id_serie']}<br>
                        PAGO: {t['codigo_pago']}<br>
                        VENDEDOR: {t['vendedor']}
                    </div>
                    <hr style="border-top: 1px dashed #000;">
                    <table style="width:100%; font-size: 10px;">
                        <tr><td>1er Premio</td><td style="text-align:right;">$500</td></tr>
                        <tr><td>2do Premio</td><td style="text-align:right;">$200</td></tr>
                    </table>
                    <p style="font-size: 9px; margin-top:10px;">Caduca en 7 días. Conserve el ticket.</p>
                </center>
            </div>
            """
            st.markdown(ticket_html, unsafe_allow_html=True)
            
            # --- BOTÓN DE IMPRESIÓN (SIN f-string para evitar error) ---
            if st.button("🖨️ IMPRIMIR / GUARDAR PDF"):
                js_print = """
                <script>
                var printContents = window.parent.document.getElementById('ticket-area').innerHTML;
                var printWindow = window.open('', '', 'height=600,width=450');
                printWindow.document.write('<html><head><style>');
                printWindow.document.write('@page { size: 80mm auto; margin: 0; }');
                printWindow.document.write('body { width: 75mm; margin: 2mm; font-family: monospace; }');
                printWindow.document.write('</style></head><body>');
                printWindow.document.write(printContents);
                printWindow.document.write('</body></html>');
                printWindow.document.close();
                setTimeout(function() {
                    printWindow.print();
                    printWindow.close();
                }, 500);
                </script>
                """
                components.html(js_print, height=0)

elif choice == "Finanzas Globales":
    st.header("📈 Reportes Financieros")
    df = st.session_state.db_ventas
    c1, c2, c3 = st.columns(3)
    c1.metric("Recaudación Total", f"${df['monto'].sum():.2f}")
    c2.metric("Tickets Emitidos", len(df))
    c3.metric("Tickets Caducados", "0")
    
    st.subheader("Ventas por Vendedor")
    if not df.empty:
        st.table(df.groupby('vendedor')['monto'].sum())

elif choice == "Gestionar Vendedores":
    st.header("👥 Administración de Puntos de Venta")
    with st.expander("Crear Nuevo Punto de Venta"):
        nu = st.text_input("Usuario")
        nc = st.text_input("Clave")
        if st.button("Guardar Vendedor"):
            nueva_fila = {'usuario': nu, 'clave': nc, 'rol': 'Punto de Venta', 'estado': 'Activo'}
            st.session_state.puntos_venta = pd.concat([st.session_state.puntos_venta, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Vendedor Agregado")
    st.dataframe(st.session_state.puntos_venta, use_container_width=True)

# --- CONFIGURACIÓN DE SORTEO (MODIFICABLE POR ADMIN) ---
elif choice == "Configurar Sorteo":
    st.header("⚙️ Configuración Global")
    st.text_input("Nombre del Sorteo", "Gran Rifa 2024")
    st.date_input("Fecha del Sorteo")
    st.number_input("Rango Máximo", 0, 9999, 99)
    st.button("Actualizar Parámetros")