import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Rifas Pro", layout="wide")

# --- ESTILOS CSS (Simulando Dashboard Admin) ---
st.markdown("""
<style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #28a745;
    }
    .ticket-print {
        width: 80mm; padding: 10px; border: 1px dashed black;
        font-family: 'Courier New', Courier, monospace; font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE CONEXIÓN (MOCK para demostración) ---
# En producción usar: conn = st.connection("gsheets", type=GSheetsConnection)
if 'db_ventas' not in st.session_state:
    st.session_state.db_ventas = pd.DataFrame(columns=[
        'id_serie', 'codigo_pago', 'numero', 'vendedor', 'monto', 'fecha', 'hora', 'estado'
    ])
if 'puntos_venta' not in st.session_state:
    st.session_state.puntos_venta = pd.DataFrame([
        {'usuario': 'admin', 'clave': '1234', 'rol': 'Super Admin', 'estado': 'Activo'},
        {'usuario': 'pos_central', 'clave': '5678', 'rol': 'Punto de Venta', 'estado': 'Activo'}
    ])

# --- AUTENTICACIÓN ---
if 'user' not in st.session_state:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        match = st.session_state.puntos_venta[
            (st.session_state.puntos_venta['usuario'] == user) & 
            (st.session_state.puntos_venta['clave'] == pw) &
            (st.session_state.puntos_venta['estado'] == 'Activo')
        ]
        if not match.empty:
            st.session_state.user = user
            st.session_state.rol = match.iloc[0]['rol']
            st.rerun()
        else:
            st.error("Credenciales incorrectas o usuario bloqueado")
    st.stop()

# --- BARRA LATERAL (MENÚ) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3408/3408506.png", width=100)
    st.title(f"Bienvenido, {st.session_state.user}")
    st.info(f"Rol: {st.session_state.rol}")
    
    menu = ["Inicio", "Comprar/Vender", "Mis Tickets"]
    if st.session_state.rol == "Super Admin":
        menu += ["--- ADMIN ---", "Puntos de Venta", "Configurar Sorteo", "Finanzas", "Ganadores"]
    
    choice = st.radio("Navegación", menu)
    if st.button("Cerrar Sesión"):
        del st.session_state.user
        st.rerun()

# --- MÓDULO: COMPRAR / VENDER ---
if choice == "Comprar/Vender":
    st.header("🎟️ Emisión de Tickets")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Selección")
        num_ticket = st.number_input("Número (00-99)", min_value=0, max_value=99, format="%02d")
        monto = st.selectbox("Monto de Apuesta", [1.00, 2.00, 5.00, 10.00])
        
        if st.button("Generar Venta"):
            serie = str(uuid.uuid4())[:8].upper()
            codigo = f"PAY-{random.randint(1000, 9999)}"
            nueva_venta = {
                'id_serie': serie, 'codigo_pago': codigo, 'numero': f"{num_ticket:02d}",
                'vendedor': st.session_state.user, 'monto': monto,
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'hora': datetime.now().strftime("%H:%M:%S"), 'estado': 'Activo'
            }
            st.session_state.db_ventas = pd.concat([st.session_state.db_ventas, pd.DataFrame([nueva_venta])], ignore_index=True)
            st.success(f"Ticket {num_ticket:02d} vendido con éxito")
            st.session_state.ultimo_ticket = nueva_venta

    with col2:
        if 'ultimo_ticket' in st.session_state:
            t = st.session_state.ultimo_ticket
            st.subheader("Vista Previa POS (80mm)")
            ticket_html = f"""
            <div style="background: white; color: black; padding: 10px; border: 1px solid #ccc; width: 300px; font-family: monospace;">
                <center>
                    <h2 style="margin:0;">Lotería Fortuna</h2>
                    <p>RIFA ACTIVA #001</p>
                    <hr>
                    <h1 style="font-size: 40px; margin: 10px 0;">{t['numero']}</h1>
                    <p>VALOR: ${t['monto']}</p>
                    <hr>
                    <div style="text-align: left; font-size: 10px;">
                        FECHA: {t['fecha']} {t['hora']}<br>
                        SERIE: {t['id_serie']}<br>
                        COD. PAGO: {t['codigo_pago']}<br>
                        VENDEDOR: {t['vendedor']}
                    </div>
                    <hr>
                    <table style="width:100%; font-size: 10px;">
                        <tr><td>1er Lugar</td><td>$500</td></tr>
                        <tr><td>2do Lugar</td><td>$200</td></tr>
                        <tr><td>3er Lugar</td><td>$100</td></tr>
                    </table>
                </center>
            </div>
            """
            st.markdown(ticket_html, unsafe_allow_html=True)
            st.button("🖨️ Imprimir Ticket (POS 80mm)")

# --- MÓDULO: PUNTOS DE VENTA (SÓLO ADMIN) ---
elif choice == "Puntos de Venta":
    st.header("🏪 Gestión de Puntos de Venta")
    
    with st.expander("➕ Crear Nuevo Vendedor"):
        new_u = st.text_input("Usuario Vendedor")
        new_p = st.text_input("Contraseña Vendedor")
        if st.button("Registrar"):
            new_row = {'usuario': new_u, 'clave': new_p, 'rol': 'Punto de Venta', 'estado': 'Activo'}
            st.session_state.puntos_venta = pd.concat([st.session_state.puntos_venta, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Vendedor creado")

    st.dataframe(st.session_state.puntos_venta, use_container_width=True)

# --- MÓDULO: FINANZAS ---
elif choice == "Finanzas":
    st.header("📊 Reporte Financiero")
    
    df = st.session_state.db_ventas
    total_recaudado = df['monto'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Recaudado", f"${total_recaudado:.2f}")
    c2.metric("Tickets Vendidos", len(df))
    c3.metric("Tickets Caducados (7 días)", "0")

    st.subheader("Ventas por Punto de Venta")
    ventas_puntos = df.groupby('vendedor')['monto'].sum().reset_index()
    st.table(ventas_puntos)

# --- MÓDULO: GANADORES ---
elif choice == "Ganadores":
    st.header("🏆 Lista de Ganadores")
    # Simulación de tabla de ganadores
    ganadores_mock = pd.DataFrame({
        'Numero': ['24', '88'],
        'Premio': ['$500.00', '$200.00'],
        'Serie': ['A1B2C3', 'D4E5F6'],
        'Fecha Pago': ['2023-10-25', 'Pendiente']
    })
    st.dataframe(ganadores_mock, use_container_width=True)

# --- INICIO ---
elif choice == "Inicio":
    st.title("🏠 Tablero Principal")
    col1, col2 = st.columns(2)
    with col1:
        st.info("### Próximo Sorteo: 31 de Diciembre")
    with col2:
        st.success("### Pozo Acumulado: $5,000")
import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import streamlit.components.v1 as components
# BOTÓN DE IMPRESIÓN (Versión Segura sin f-string para evitar SyntaxError)
    if st.button("🔥 IMPRIMIR EN POS-80"):
        # Extraemos los datos necesarios para inyectarlos limpiamente
        js_numero = t['numero']
        js_monto = t['monto']
        js_fecha = t['fecha']
        js_serie = t['id_serie']
        js_pago = t['codigo_pago']

        # Usamos una cadena normal y format() para evitar conflictos con llaves de JS/CSS
        js_code = """
            <script>
            var printContents = window.parent.document.getElementById('ticket-area').innerHTML;
            var printWindow = window.open('', '', 'height=600,width=450');
            printWindow.document.write('<html><head><style>');
            printWindow.document.write('@page { size: 80mm auto; margin: 0; }');
            printWindow.document.write('body { width: 75mm; margin: 2mm; font-family: monospace; font-size: 12px; }');
            printWindow.document.write('</style></head><body>');
            printWindow.document.write(printContents);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            
            // Pequeña pausa para asegurar que el contenido cargue antes de imprimir
            setTimeout(function() {
                printWindow.print();
                printWindow.close();
            }, 500);
            </script>
        """
        components.html(js_code, height=0)