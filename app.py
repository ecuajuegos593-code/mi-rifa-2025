import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Admin Rifas Pro 2025", layout="wide", page_icon="🎟️")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Nota: Requiere configuración de st.secrets para funcionar en la nube
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_ventas = conn.read(worksheet="ventas")
except Exception:
    # Backup local si no hay conexión para que la app no rompa
    if 'db_ventas' not in st.session_state:
        st.session_state.db_ventas = pd.DataFrame(columns=[
            'id_serie', 'codigo_pago', 'numero', 'vendedor', 'monto', 'fecha', 'hora', 'estado'
        ])
    df_ventas = st.session_state.db_ventas

# --- FUNCIONES DE LÓGICA ---
def verificar_caducidad(fecha_str):
    """Calcula si han pasado más de 7 días desde la compra"""
    fecha_ticket = datetime.strptime(fecha_str, "%Y-%m-%d")
    if datetime.now() > fecha_ticket + timedelta(days=7):
        return "CADUCADO"
    return "VIGENTE"

# --- USUARIOS Y SEGURIDAD ---
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = pd.DataFrame([
        {'usuario': 'admin', 'clave': 'admin123', 'rol': 'Super Admin', 'estado': 'Activo'},
        {'usuario': 'vendedor01', 'clave': 'pos80', 'rol': 'Punto de Venta', 'estado': 'Activo'}
    ])

# --- LOGIN ---
if 'user' not in st.session_state:
    st.title("🔐 Acceso al Sistema")
    with st.container():
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            match = st.session_state.usuarios[
                (st.session_state.usuarios['usuario'] == u) & 
                (st.session_state.usuarios['clave'] == p) & 
                (st.session_state.usuarios['estado'] == 'Activo')
            ]
            if not match.empty:
                st.session_state.user = u
                st.session_state.rol = match.iloc[0]['rol']
                st.rerun()
            else:
                st.error("Credenciales inválidas o usuario bloqueado.")
    st.stop()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🎟️ RifaPanel")
    st.write(f"Usuario: **{st.session_state.user}**")
    st.write(f"Rol: `{st.session_state.rol}`")
    st.divider()
    
    opciones = ["Inicio", "Vender Ticket", "Mis Reportes", "Validar Ganador"]
    if st.session_state.rol == "Super Admin":
        opciones += ["--- ADMIN ---", "Puntos de Venta", "Finanzas", "Configurar Sorteo"]
    
    menu = st.radio("Navegación", opciones)
    
    if st.button("Cerrar Sesión"):
        del st.session_state.user
        st.rerun()

# --- CONTENIDO PRINCIPAL ---

if menu == "Inicio":
    st.title("📊 Dashboard General")
    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas Totales", len(df_ventas))
    c2.metric("Recaudación", f"${df_ventas['monto'].astype(float).sum():.2f}")
    c3.metric("Sorteo", "Activo")

elif menu == "Vender Ticket":
    st.header("🛒 Nueva Venta")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        num_elegido = st.number_input("Número (00-99)", 0, 99, format="%02d")
        monto_rifa = st.selectbox("Monto", [1.0, 2.0, 5.0, 10.0])
        
        if st.button("Generar Ticket"):
            serie = str(uuid.uuid4())[:8].upper()
            codigo = f"XP-{random.randint(1000, 9999)}"
            nueva_v = {
                'id_serie': serie, 'codigo_pago': codigo, 'numero': f"{num_elegido:02d}",
                'vendedor': st.session_state.user, 'monto': monto_rifa,
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'hora': datetime.now().strftime("%H:%M:%S"), 'estado': 'VIGENTE'
            }
            # Guardar (aquí se añadiría conn.update si usas GSheets)
            st.session_state.db_ventas = pd.concat([df_ventas, pd.DataFrame([nueva_v])], ignore_index=True)
            st.session_state.ultimo_ticket = nueva_v
            st.success("¡Venta registrada!")

    with col2:
        if 'ultimo_ticket' in st.session_state:
            t = st.session_state.ultimo_ticket
            ticket_html = f"""
            <div id="ticket-area" style="width: 75mm; padding: 10px; border: 1px solid black; background: white; color: black; font-family: 'Courier New', monospace;">
                <center>
                    <h2 style="margin:0;">RIFA EXPRESS</h2>
                    <hr>
                    <p style="font-size:12px;">TICKET DE VENTA</p>
                    <h1 style="font-size:45px; margin:5px;">{t['numero']}</h1>
                    <p style="font-size:18px;">MONTO: ${t['monto']}</p>
                    <hr>
                    <div style="text-align:left; font-size:11px;">
                        FECHA: {t['fecha']} {t['hora']}<br>
                        SERIE: {t['id_serie']}<br>
                        CODIGO: {t['codigo_pago']}<br>
                        VENDEDOR: {t['vendedor']}
                    </div>
                    <hr>
                    <p style="font-size:10px;">Válido por 7 días. Conserve este comprobante para cobrar su premio.</p>
                </center>
            </div>
            """
            st.markdown(ticket_html, unsafe_allow_html=True)
            
            if st.button("🖨️ Imprimir POS-80 / PDF"):
                js_print = """
                <script>
                var content = window.parent.document.getElementById('ticket-area').innerHTML;
                var win = window.open('', '', 'height=600,width=450');
                win.document.write('<html><head><style>@page { size: 80mm auto; margin: 0; } body { width: 75mm; margin: 2mm; font-family: monospace; }</style></head><body>');
                win.document.write(content);
                win.document.write('</body></html>');
                win.document.close();
                setTimeout(function(){ win.print(); win.close(); }, 500);
                </script>
                """
                components.html(js_print, height=0)

elif menu == "Validar Ganador":
    st.header("🏆 Validación de Tickets")
    s_in = st.text_input("Número de Serie")
    c_in = st.text_input("Código de Pago")
    
    if st.button("Verificar"):
        res = df_ventas[(df_ventas['id_serie'] == s_in) & (df_ventas['codigo_pago'] == c_in)]
        if not res.empty:
            vigencia = verificar_caducidad(res.iloc[0]['fecha'])
            if vigencia == "VIGENTE":
                st.success(f"✅ Ticket VÁLIDO. Número: {res.iloc[0]['numero']}")
            else:
                st.error("❌ Ticket CADUCADO (Excedió los 7 días).")
        else:
            st.error("Ticket no encontrado.")

elif menu == "Finanzas":
    st.header("💰 Reporte de Ingresos")
    df_ventas['caducidad'] = df_ventas['fecha'].apply(verificar_caducidad)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Ventas por Vendedor")
        st.bar_chart(df_ventas.groupby('vendedor')['monto'].sum())
    with c2:
        st.subheader("Estado de Tickets")
        st.write(df_ventas['caducidad'].value_counts())
    
    st.dataframe(df_ventas, use_container_width=True)

elif menu == "Puntos de Venta":
    st.header("👥 Gestión de Usuarios")
    st.dataframe(st.session_state.usuarios)
    
    with st.expander("Bloquear/Desbloquear Vendedor"):
        user_to_mod = st.selectbox("Seleccionar Vendedor", st.session_state.usuarios['usuario'])
        if st.button("Cambiar Estado"):
            idx = st.session_state.usuarios[st.session_state.usuarios['usuario'] == user_to_mod].index
            current = st.session_state.usuarios.at[idx[0], 'estado']
            st.session_state.usuarios.at[idx[0], 'estado'] = "Inactivo" if current == "Activo" else "Activo"
            st.success("Estado actualizado.")
            st.rerun()

elif menu == "Configurar Sorteo":
    st.header("⚙️ Configuración Global")
    nombre_rifa = st.text_input("Nombre de la Rifa", "Sorteo Relámpago")
    rango = st.slider("Rango de Números", 0, 999, 99)
    st.button("Guardar Configuración")