import streamlit as st
from logic.triage import prioridad_num

def render_hospital():
    st.title("👨‍⚕️ Panel de Fila de Espera")
    st.write("Vista para el personal del hospital (simulación).")

    fila = st.session_state.get("fila_espera", [])
    if not fila:
        st.info("No hay pacientes en espera.")
        return

    fila_ordenada = sorted(
        fila,
        key=lambda p: (prioridad_num(p["categoria"]), p["hora_llegada"])
    )

    st.subheader("Pacientes en espera (ordenados por prioridad)")
    st.table([
        {
            "Ticket": p["ticket"],
            "RUT": p["rut"],
            "Nombre": f"{p['nombre']} {p['apellido']}",
            "Triage": p["categoria"],
            "Hora llegada": p["hora_llegada"],
            "Motivo": p["motivo"][:40] + ("..." if len(p["motivo"]) > 40 else "")
        }
        for p in fila_ordenada
    ])
