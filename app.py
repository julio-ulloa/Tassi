import streamlit as st
from ui.styles import inject_global_styles
from ui.kiosk import render_kiosko
from ui.hospital import render_hospital

def init_state():
    if "pacientes" not in st.session_state:
        st.session_state["pacientes"] = {
            "11.111.111-1": {"nombre": "Juan", "apellido": "Pérez", "fecha_nacimiento": "1990-01-01"},
            "22.222.222-2": {"nombre": "María", "apellido": "González", "fecha_nacimiento": "1985-05-10"},
        }
    if "fila_espera" not in st.session_state:
        st.session_state["fila_espera"] = []
    if "rut_actual" not in st.session_state:
        st.session_state["rut_actual"] = None
    if "paciente_actual" not in st.session_state:
        st.session_state["paciente_actual"] = None

    # defaults signos vitales (widgets)
    if "k_temp" not in st.session_state: st.session_state["k_temp"] = 37.0
    if "k_fc" not in st.session_state: st.session_state["k_fc"] = 80
    if "k_pas" not in st.session_state: st.session_state["k_pas"] = 120
    if "k_pad" not in st.session_state: st.session_state["k_pad"] = 80
    if "k_spo2" not in st.session_state: st.session_state["k_spo2"] = 98
    if "k_dolor" not in st.session_state: st.session_state["k_dolor"] = 3

def main():
    st.set_page_config(page_title="Simulación Kiosko de Triage", page_icon="🏥", layout="wide")
    inject_global_styles()
    init_state()

    st.sidebar.title("Navegación")
    modo = st.sidebar.radio("Selecciona el modo:", ("Kiosko paciente", "Vista hospital"))

    if modo == "Kiosko paciente":
        render_kiosko()
    else:
        render_hospital()

if __name__ == "__main__":
    main()
