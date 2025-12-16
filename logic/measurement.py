import time
import random
from datetime import datetime
import streamlit as st

def ensure_measurement_state():
    if "machine_state" not in st.session_state:
        st.session_state["machine_state"] = "IDLE"  # IDLE | MEASURING | DONE
    if "k_last_measure" not in st.session_state:
        st.session_state["k_last_measure"] = None

def medir_con_escaneo():
    st.session_state["machine_state"] = "MEASURING"

    with st.spinner("🌡️ Midiendo temperatura..."):
        time.sleep(1.2)
        st.session_state["k_temp"] = round(random.uniform(36.0, 39.6), 1)

    with st.spinner("💓 Midiendo frecuencia cardiaca..."):
        time.sleep(1.2)
        st.session_state["k_fc"] = random.randint(60, 125)

    with st.spinner("🩸 Midiendo presión arterial..."):
        time.sleep(1.6)
        st.session_state["k_pas"] = random.randint(90, 165)
        st.session_state["k_pad"] = random.randint(60, 105)

    with st.spinner("🫁 Midiendo saturación de oxígeno..."):
        time.sleep(1.1)
        st.session_state["k_spo2"] = random.randint(90, 100)

    with st.spinner("🧠 Registrando nivel de dolor..."):
        time.sleep(0.9)
        st.session_state["k_dolor"] = random.randint(0, 10)

    st.session_state["k_last_measure"] = datetime.now().strftime("%H:%M:%S")
    st.session_state["machine_state"] = "DONE"

def reset_medicion():
    st.session_state["machine_state"] = "IDLE"
    st.session_state["k_last_measure"] = None
