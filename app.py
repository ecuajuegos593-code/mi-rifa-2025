import streamlit as st
import random
import time
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="RifaPro - Sistema de Lotería", layout="wide")

# --- SIMULACIÓN DE BASE DE DATOS (En producción usar SQL) ---
if 'numbers' not in st.session_state:
    # Generamos 100 números: 0 = Libre, 1 = Apartado, 2 = Vendido
    st.session_state.numbers = {i: {"status": 0, "expires": None} for i in range(100)}

# --- LÓGICA DE LIMPIEZA DE APARTADOS ---
def update_expirations():
    now = datetime.now()
    for num, data in st.session_state.numbers.items():
        if data["status"] == 1 and data["expires"] < now:
            st.session_state.numbers[num] = {"status": 0, "expires": None}

update_expirations()

# --- INTERFAZ DE USUARIO ---
st.title("🎟️ RifaPro: Adquiere tu número de la suerte")
st.markdown("Selecciona tus números, completa el pago y asegura tu participación.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Talonario Digital")
    # Mostrar leyenda
    c1, c2, c3 = st.columns(3)
    c1.info("🟢 Libre")
    c2.warning("🟡 Apartado")
    c3.error("🔴 Vendido")

    # Renderizar cuadrícula de números (10x10)
    cols = st.columns(10)
    for i in range(100):
        num_data = st.session_state.numbers[i]
        status = num_data["status"]
        
        label = f"{i:02d}"
        
        if status == 0:
            if cols[i % 10].button(label, key=f"btn_{i}", use_container_width=True):
                # Apartar número por 15 minutos
                st.session_state.numbers[i] = {
                    "status": 1, 
                    "expires": datetime.now() + timedelta(minutes=15)
                }
                st.rerun()
        elif status == 1:
            cols[i % 10].button(label, key=f"btn_{i}", disabled=True, type="secondary", help="Apartado temporalmente")
        else:
            cols[i % 10].button(label, key=f"btn_{i}", disabled=True, type="primary")

with col2:
    st.subheader("Gestión de Compra")
    apartados = [n for n, d in st.session_state.numbers.items() if d["status"] == 1]
    
    if not apartados:
        st.write("No has seleccionado números aún.")
    else:
        st.write(f"Has seleccionado: **{len(apartados)} números**")
        st.code(", ".join([f"{n:02d}" for n in apartados]))
        
        nombre = st.text_input("Nombre completo")
        whatsapp = st.text_input("WhatsApp (para enviar comprobante)")
        
        metodo = st.selectbox("Método de Pago", ["Transferencia Bancaria", "PayPal", "Mercado Pago"])
        
        if st.button("Confirmar Pago y Finalizar"):
            if nombre and whatsapp:
                for n in apartados:
                    st.session_state.numbers[n] = {"status": 2, "expires": None}
                st.success(f"¡Gracias {nombre}! Tus números han sido registrados. Recibirás un mensaje al {whatsapp}")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Por favor completa tus datos.")

# --- SECCIÓN DE ADMINISTRACIÓN (OCULTA O PROTEGIDA) ---
st.divider()
with st.expander("⚙️ Panel de Control (Admin)"):
    if st.button("Resetear Todo el Talonario"):
        st.session_state.numbers = {i: {"status": 0, "expires": None} for i in range(100)}
        st.rerun()