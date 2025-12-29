import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random
import streamlit.components.v1 as components
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Rifas PRO", layout="wide", page_icon="🎟️")

# --- ESTILOS PARA INTERFAZ ---
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #28a745; }
    .ticket-box { 
        width: 80mm; padding: 10px; border: 1px solid black; 
        background: white; color: black; font-family: 'Courier New', monospace; 
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE BASE DE DATOS (Sesión) ---
if 'db_ventas' not in st.session_state:
    st.session_state.db_ventas = pd.DataFrame(columns=[
        'id_serie', 'codigo_pago', 'numero', 'vendedor', 'monto', 'fecha', 'hora', 'estado'
    ])

if 'usuarios' not in st.session_state:
    st.session_state.usuarios = pd.DataFrame([
        {'usuario': 'admin', 'clave': 'admin2025', 'rol': 'Super Admin', 'estado': 'Activo'},
        {'usuario': 'punto01', 'clave': 'venta01', 'rol': 'Punto de Venta', 'estado': 'Activo'}
    ])

# --- FUNCIONES LÓGICAS ---
def verificar_vigencia(fecha_str):
    fecha_t = datetime.strptime(fecha_str, "%Y-%m-%d")
    return "VIGENTE" if (datetime.now() - fecha_t).days <= 7 else "CADUCADO"

# --- SISTEMA DE LOGIN ---
if 'user' not in st.session_state:
    st.title("🔐 Acceso Administrativo")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
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
            st.error("Acceso denegado.")
    st.stop()

# --- BARRA LATERAL (MENÚ) ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    st.caption(f"Rol: {st.session_state.rol}")
    st.divider()
    
    opciones = ["🏠 Inicio", "🛒 Comprar/Vender", "📋 Mis Tickets", "🏆 Validar Ganador"]
    if st.session_state.rol == "Super Admin":
        opciones += ["📍 Puntos de Venta", "⚙️ Configurar Sorteo", "📊 Finanzas Globales"]
    
    choice = st.radio("Menú de Navegación", opciones)
    
    if st.button("🚪 Cerrar Sesión"):
        del st.session_state.user
        st.rerun()

# --- SECCIÓN: INICIO ---
if "Inicio" in choice:
    st.title("Panel de Control")
    df = st.session_state.db_ventas
    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas Totales", f"{len(df)}")
    c2.metric("Recaudado", f"${df['monto'].sum():.2f}")
    c3.metric("Sorteo Activo", "00 - 99")

# --- SECCIÓN: COMPRAR / VENDER ---
elif "Comprar/Vender" in choice:
    st.title("Emitir Nuevo Ticket")
    col_v1, col_v2 = st.columns([1, 1.2])
    
    with col_v1:
        num = st.number_input("Seleccionar Número (00-99)", 0, 99, format="%02d")
        monto = st.selectbox("Valor del Ticket", [1.0, 2.0, 5.0, 10.0])
        
        if st.button("🔥 Generar Venta e Imprimir"):
            serie = str(uuid.uuid4())[:8].upper()
            codigo = f"XP-{random.randint(1000, 9999)}"
            nueva_venta = {
                'id_serie': serie, 'codigo_pago': codigo, 'numero': f"{num:02d}",
                'vendedor': st.session_state.user, 'monto': monto,
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'hora': datetime.now().strftime("%H:%M:%S"), 'estado': 'Activo'
            }
            st.session_state.db_ventas = pd.concat([st.session_state.db_ventas, pd.DataFrame([nueva_venta])], ignore_index=True)
            st.session_state.ultimo_ticket = nueva_venta
            st.success("Ticket registrado en el sistema.")

    with col_v2:
        if 'ultimo_ticket' in st.session_state:
            t = st.session_state.ultimo_ticket
            ticket_html = f"""
            <div id="ticket-area" style="width: 75mm; padding: 10px; border: 1px solid #000; background: white; color: black; font-family: monospace; text-align: center;">
                <h2 style="margin:0;">Lotería Fortuna</h2>
                <p style="font-size:10px;">Comprobante Oficial</p>
                <hr style="border-top: 1px dashed black;">
                <span style="font-size:14px;">NÚMERO JUGADO</span><br>
                <span style="font-size:48px; font-weight:bold;">{t['numero']}</span><br>
                <span style="font-size:20px;">VALOR: ${t['monto']}</span>
                <hr style="border-top: 1px dashed black;">
                <div style="text-align: left; font-size: 11px;">
                    FECHA: {t['fecha']} {t['hora']}<br>
                    SERIE: {t['id_serie']}<br>
                    COD. PAGO: {t['codigo_pago']}<br>
                    VENDEDOR: {t['vendedor']}
                </div>
                <hr style="border-top: 1px dashed black;">
                <table style="width:100%; font-size: 10px; text-align: left;">
                    <tr><td>1er Premio</td><td style="text-align:right;">$500.00</td></tr>
                    <tr><td>2do Premio</td><td style="text-align:right;">$200.00</td></tr>
                </table>
                <p style="font-size: 9px; margin-top:10px;">Ticket válido por 7 días calendario.</p>
            </div>
            """
            st.markdown(ticket_html, unsafe_allow_html=True)
            
            # Botón de Impresión Directa
            if st.button("🖨️ IMPRIMIR EN POS-80"):
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

# --- SECCIÓN: VALIDAR GANADOR ---
elif "Validar Ganador" in choice:
    st.title("🏆 Verificación de Tickets")
    serie_check = st.text_input("Número de Serie")
    cod_check = st.text_input("Código de Pago Único")
    
    if st.button("🔍 Validar Ticket"):
        res = st.session_state.db_ventas[
            (st.session_state.db_ventas['id_serie'] == serie_check) & 
            (st.session_state.db_ventas['codigo_pago'] == cod_check)
        ]
        
        if not res.empty:
            vigencia = verificar_vigencia(res.iloc[0]['fecha'])
            if vigencia == "VIGENTE":
                st.success(f"✅ TICKET VÁLIDO. Número: {res.iloc[0]['numero']} | Emitido el: {res.iloc[0]['fecha']}")
            else:
                st.error("❌ TICKET CADUCADO. Han pasado más de 7 días.")
        else:
            st.warning("No se encontró ningún ticket con esos datos.")

# --- SECCIÓN: FINANZAS (SUPER ADMIN) ---
elif "Finanzas Globales" in choice:
    st.title("📊 Reportes Financieros")
    df = st.session_state.db_ventas
    df['Vigencia'] = df['fecha'].apply(verificar_vigencia)
    
    st.subheader("Resumen de Ventas")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Reporte por Vendedor")
    st.table(df.groupby('vendedor')['monto'].sum())

# --- SECCIÓN: PUNTOS DE VENTA (SUPER ADMIN) ---
elif "Puntos de Venta" in choice:
    st.title("👥 Gestión de Vendedores")
    st.dataframe(st.session_state.usuarios, use_container_width=True)
    
    with st.expander("Modificar Estado de Vendedor"):
        user_sel = st.selectbox("Vendedor", st.session_state.usuarios['usuario'])
        if st.button("Bloquear / Activar"):
            idx = st.session_state.usuarios[st.session_state.usuarios['usuario'] == user_sel].index
            curr = st.session_state.usuarios.at[idx[0], 'estado']
            st.session_state.usuarios.at[idx[0], 'estado'] = "Inactivo" if curr == "Activo" else "Activo"
            st.rerun()

# --- SECCIÓN: CONFIGURAR SORTEO (SUPER ADMIN) ---
elif "Configurar Sorteo" in choice:
    st.title("⚙️ Parámetros Globales")
    st.text_input("Nombre de la Rifa", "Sorteo Extraordinario")
    st.number_input("Cantidad de Números", 10, 1000, 100)
    st.date_input("Fecha del Sorteo")
    st.button("Actualizar Parámetros")