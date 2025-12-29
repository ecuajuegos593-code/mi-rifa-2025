import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE ESTILO INSPIRADO EN TU HTML ---
st.set_page_config(page_title="APT3 - Sistema de Ventas", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.13.0/css/all.min.css">
    <style>
        .main { background-color: #f4f6f9; }
        .sidebar .sidebar-content { background-image: linear-gradient(#23272d,#23272d); color: white; }
        .stButton>button { width: 100%; border-radius: 4px; height: 3em; font-size: 1.2em; background-color: #343a40; color: white; }
        .card { 
            background-color: white; padding: 20px; border-radius: 5px; 
            border: 1px solid #dee2e6; box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
            margin-bottom: 20px;
        }
        .header-top { background-color: #ffffff; padding: 10px; border-bottom: 2px solid #3d464d; margin-bottom: 20px; }
        .input-group-text { background-color: transparent; border: none; color: #6c757d; }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
if 'db_ventas' not in st.session_state:
    st.session_state.db_ventas = pd.DataFrame(columns=[
        'id_serie', 'codigo_pago', 'numero', 'loteria', 'monto', 'fecha', 'hora', 'estado'
    ])

# --- BARRA LATERAL (SIDEBAR DE TU HTML) ---
with st.sidebar:
    st.image("http://52.201.2.30/apt3/assets/img/logo3.png", width=150)
    st.markdown("---")
    menu = st.radio("MENÚ", ["🛒 Vender", "📊 Reportes", "🏆 Pago de Premios", "⏳ Caducados", "⚙️ Admin Reportes", "❌ Finalizar"])
    st.markdown("---")
    st.write("👤 Usuario: **OPTAYLORSD**")

if menu == "❌ Finalizar":
    st.session_state.clear()
    st.rerun()

# --- HEADER SUPERIOR ---
st.markdown("""<div class='header-top'><h3><i class="fa fa-shopping-cart"></i> Ventas / Listado</h3></div>""", unsafe_allow_html=True)

# --- CUERPO PRINCIPAL ---
if menu == "🛒 Vender":
    col_izq, col_der = st.columns([1, 1.5])

    with col_izq:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Venta de Tickets")
        
        # Fecha (como tu input id="date")
        fecha_venta = st.date_input("Fecha Sorteo", datetime.now())
        
        # Lotería (como tu select id="loterias")
        loteria = st.selectbox("Selecciona la Lotería", ["Lotería Nacional", "Rifa Local", "Sorteo Extra"])
        
        # Número (como tu input id="number")
        # Cambiado a 00-99 según tu solicitud inicial
        num = st.text_input("🔢 Número (00-99)", placeholder="Ej: 57", max_chars=2)
        
        # Valor (como tu input id="value")
        valor = st.number_input("💵 Valor ($)", min_value=0.0, step=1.0)
        
        if st.button("VENDER"):
            if len(num) == 2 and valor > 0:
                serie = str(uuid.uuid4())[:8].upper()
                codigo = f"PAY-{random.randint(1000, 9999)}"
                nueva_v = {
                    'id_serie': serie, 'codigo_pago': codigo, 'numero': num,
                    'loteria': loteria, 'monto': valor,
                    'fecha': fecha_venta.strftime("%Y-%m-%d"),
                    'hora': datetime.now().strftime("%H:%M:%S"), 'estado': 'VIGENTE'
                }
                st.session_state.db_ventas = pd.concat([st.session_state.db_ventas, pd.DataFrame([nueva_v])], ignore_index=True)
                st.session_state.ultimo_ticket = nueva_v
                st.success("Venta procesada con éxito")
            else:
                st.error("Error: Verifique el número y el valor.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_der:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Resumen / Impresión")
        
        if 'ultimo_ticket' in st.session_state:
            t = st.session_state.ultimo_ticket
            # Contenedor para el Ticket (POS80)
            ticket_ui = f"""
            <div id="ticket-area" style="width: 75mm; padding: 10px; border: 1px dashed #000; background: white; color: black; font-family: monospace;">
                <center>
                    <img src="http://52.201.2.30/apt3/assets/img/logo3.png" style="width: 100px;"><br>
                    <strong>TICKET DE VENTA</strong><br>
                    <h1 style="margin: 5px 0; font-size: 50px;">{t['numero']}</h1>
                    <p style="font-size: 20px;">VALOR: ${t['monto']}</p>
                    <hr>
                    <div style="text-align: left; font-size: 11px;">
                        FECHA: {t['fecha']} {t['hora']}<br>
                        SERIE: {t['id_serie']}<br>
                        PIN PAGO: {t['codigo_pago']}<br>
                        LOTERIA: {t['loteria']}
                    </div>
                    <hr>
                    <table style="width:100%; font-size: 10px;">
                        <tr><td>1er Premio</td><td>$500</td></tr>
                        <tr><td>2do Premio</td><td>$200</td></tr>
                    </table>
                    <p style="font-size: 9px; margin-top:10px;">Válido por 7 días.</p>
                </center>
            </div>
            """
            st.markdown(ticket_ui, unsafe_allow_html=True)
            
            # Script de impresión
            if st.button("🖨️ IMPRIMIR TICKET"):
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
        else:
            st.info("Esperando venta para generar ticket...")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "⏳ Caducados":
    st.subheader("Tickets Caducados (7 días)")
    df = st.session_state.db_ventas.copy()
    # Lógica de cálculo
    df['fecha_dt'] = pd.to_datetime(df['fecha'])
    df['dias_pasados'] = (datetime.now() - df['fecha_dt']).dt.days
    caducados = df[df['dias_pasados'] > 7]
    st.dataframe(caducados, use_container_width=True)

elif menu == "🏆 Pago de Premios":
    st.subheader("Validación y Pago")
    c1, c2 = st.columns(2)
    s_id = c1.text_input("Número de Serie")
    p_id = c2.text_input("PIN de Pago")
    if st.button("Validar Pago"):
        # Buscar en la base
        res = st.session_state.db_ventas[(st.session_state.db_ventas['id_serie'] == s_id) & (st.session_state.db_ventas['codigo_pago'] == p_id)]
        if not res.empty:
            st.success(f"Ticket validado para el número: {res.iloc[0]['numero']}. Monto a pagar: $XXX")
        else:
            st.error("Ticket no encontrado o datos incorrectos.")

elif menu == "📊 Reportes":
    st.subheader("Mis Reportes de Venta")
    st.dataframe(st.session_state.db_ventas, use_container_width=True)