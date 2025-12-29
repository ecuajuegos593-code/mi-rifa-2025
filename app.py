import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Rifas Local", layout="wide")

# --- ESTILOS INSPIRADOS EN TU DISEÑO ORIGINAL (APT3) ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.0/css/all.min.css">
    <style>
        .main { background-color: #f4f6f9; }
        [data-testid="stSidebar"] { background-color: #23272d; color: white; }
        .stButton>button { width: 100%; border-radius: 4px; height: 3.5em; font-size: 1.1em; background-color: #343a40; color: white; }
        .card { 
            background-color: white; padding: 20px; border-radius: 5px; 
            border: 1px solid #dee2e6; box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
            margin-bottom: 20px;
        }
        .header-top { background-color: #ffffff; padding: 15px; border-bottom: 2px solid #3d464d; margin-bottom: 20px; color: #333; }
        .footer { text-align: right; padding: 20px; color: #888; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS LOCALES (Solo en memoria del servidor/sesión) ---
if 'db_ventas' not in st.session_state:
    st.session_state.db_ventas = pd.DataFrame(columns=[
        'id_serie', 'codigo_pago', 'numero', 'loteria', 'monto', 'fecha', 'hora', 'estado'
    ])

if 'config_sorteo' not in st.session_state:
    st.session_state.config_sorteo = {"nombre": "Sorteo Extraordinario", "rango": "00-99"}

# --- LÓGICA DE NEGOCIO LOCAL ---
def verificar_vigencia(fecha_str):
    fecha_t = datetime.strptime(fecha_str, "%Y-%m-%d")
    diferencia = datetime.now() - fecha_t
    return "VIGENTE" if diferencia.days <= 7 else "CADUCADO"

# --- MENÚ LATERAL ---
with st.sidebar:
    st.markdown("### 🏆 SISTEMA LOCAL")
    st.divider()
    menu = st.radio("NAVEGACIÓN", 
                   ["🛒 Vender", "📋 Reporte Ventas", "🏆 Pago de Premios", "⏳ Caducados", "⚙️ Configuración", "❌ Finalizar"])
    st.divider()
    st.info("Modo: Autónomo (Sin conexión externa)")

if menu == "❌ Finalizar":
    st.session_state.clear()
    st.rerun()

# --- HEADER ---
st.markdown(f"""<div class='header-top'><h2><i class="fa fa-shopping-cart"></i> {menu}</h2></div>""", unsafe_allow_html=True)

# --- SECCIONES ---

if menu == "🛒 Vender":
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        num = st.text_input("🔢 Número (00-99)", placeholder="Ej: 05", max_chars=2)
        monto = st.number_input("💵 Valor de Apuesta", min_value=1.0, step=1.0)
        loteria = st.selectbox("🎰 Lotería / Sorteo", ["Diaria Mañana", "Diaria Tarde", "Sorteo Mayor"])
        
        if st.button("CONFIRMAR VENTA"):
            if num and monto > 0:
                serie = str(uuid.uuid4())[:8].upper()
                codigo = f"PIN-{random.randint(1000, 9999)}"
                nueva_v = {
                    'id_serie': serie, 'codigo_pago': codigo, 'numero': num,
                    'loteria': loteria, 'monto': monto,
                    'fecha': datetime.now().strftime("%Y-%m-%d"),
                    'hora': datetime.now().strftime("%H:%M:%S"), 'estado': 'VIGENTE'
                }
                st.session_state.db_ventas = pd.concat([st.session_state.db_ventas, pd.DataFrame([nueva_v])], ignore_index=True)
                st.session_state.ultimo_ticket = nueva_v
                st.success("✅ Venta Guardada")
            else:
                st.warning("⚠️ Ingrese número y monto válido")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        if 'ultimo_ticket' in st.session_state:
            t = st.session_state.ultimo_ticket
            ticket_ui = f"""
            <div id="ticket-area" style="width: 75mm; padding: 10px; border: 1px solid #000; background: white; color: black; font-family: monospace;">
                <center>
                    <h2 style="margin:0;">SISTEMA LOCAL</h2>
                    <hr>
                    <span style="font-size:14px;">NÚMERO JUGADO</span><br>
                    <span style="font-size:50px; font-weight:bold;">{t['numero']}</span><br>
                    <span style="font-size:22px;">$ {t['monto']}</span>
                    <hr>
                    <div style="text-align: left; font-size: 11px;">
                        FECHA: {t['fecha']} {t['hora']}<br>
                        SERIE: {t['id_serie']}<br>
                        COD. PAGO: {t['codigo_pago']}<br>
                        LOTERIA: {t['loteria']}
                    </div>
                    <hr>
                    <p style="font-size: 9px;">Válido 7 días. Conserve el ticket.</p>
                </center>
            </div>
            """
            st.markdown(ticket_ui, unsafe_allow_html=True)
            
            if st.button("🖨️ IMPRIMIR TICKET (POS-80)"):
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

elif menu == "📋 Reporte Ventas":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(st.session_state.db_ventas, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏆 Pago de Premios":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    s_id = c1.text_input("Serie del Ticket")
    p_id = c2.text_input("Código de Pago")
    
    if st.button("VERIFICAR TICKET GANADOR"):
        df = st.session_state.db_ventas
        res = df[(df['id_serie'] == s_id) & (df['codigo_pago'] == p_id)]
        if not res.empty:
            vigencia = verificar_vigencia(res.iloc[0]['fecha'])
            if vigencia == "VIGENTE":
                st.success(f"✅ TICKET VÁLIDO. Número: {res.iloc[0]['numero']} | Premio listo para pagar.")
            else:
                st.error("❌ TICKET CADUCADO. Excedió los 7 días de vigencia.")
        else:
            st.error("Ticket no encontrado en la base local.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⏳ Caducados":
    df = st.session_state.db_ventas.copy()
    if not df.empty:
        df['vigencia'] = df['fecha'].apply(verificar_vigencia)
        caducados = df[df['vigencia'] == "CADUCADO"]
        st.warning(f"Se han encontrado {len(caducados)} tickets fuera de tiempo.")
        st.dataframe(caducados)
    else:
        st.info("No hay registros de ventas.")

elif menu == "⚙️ Configuración":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.session_state.config_sorteo['