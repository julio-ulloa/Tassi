import streamlit as st
from datetime import datetime, date
import random

# ---------------------------------------------------------
# Inicialización de estado (simula una "base de datos" en memoria)
# ---------------------------------------------------------

def init_state():
    if "pacientes" not in st.session_state:
        st.session_state["pacientes"] = {
            "11.111.111-1": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "fecha_nacimiento": "1990-01-01"
            },
            "22.222.222-2": {
                "nombre": "María",
                "apellido": "González",
                "fecha_nacimiento": "1985-05-10"
            }
        }

    if "fila_espera" not in st.session_state:
        st.session_state["fila_espera"] = []

    if "rut_actual" not in st.session_state:
        st.session_state["rut_actual"] = None

    if "paciente_actual" not in st.session_state:
        st.session_state["paciente_actual"] = None


# ---------------------------------------------------------
# Lógica de triage (simplificada, solo académico)
# ---------------------------------------------------------

def clasificar_triage(temp, pas, pad, fc, spo2, dolor):
    # Rojo
    if temp >= 39 or pas < 90 or spo2 < 90:
        return "Rojo (1)", "Riesgo vital, requiere atención inmediata"

    # Naranja
    if temp >= 38 or dolor >= 8 or pas < 100:
        return "Naranja (2)", "Urgencia alta, debe ser evaluado pronto"

    # Amarillo
    if dolor >= 5 or (37.5 <= temp < 38):
        return "Amarillo (3)", "Urgencia moderada"

    # Verde
    if dolor > 0 or temp >= 37:
        return "Verde (4)", "Urgencia leve"

    # Azul
    return "Azul (5)", "No urgente / control programable"


def prioridad_num(categoria: str) -> int:
    try:
        return int(categoria.split("(")[1].split(")")[0])
    except Exception:
        return 99


# ---------------------------------------------------------
# Auxiliares
# ---------------------------------------------------------

def generar_numero_ticket():
    return f"T-{random.randint(1000, 9999)}"


def registrar_paciente(rut, nombre, apellido, fecha_nac: date):
    st.session_state["pacientes"][rut] = {
        "nombre": nombre,
        "apellido": apellido,
        "fecha_nacimiento": fecha_nac.strftime("%Y-%m-%d")
    }


def agregar_a_fila(rut, categoria, desc_categoria, motivo):
    datos_paciente = st.session_state["pacientes"][rut]
    ticket = generar_numero_ticket()
    hora_llegada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    atencion = {
        "ticket": ticket,
        "rut": rut,
        "nombre": datos_paciente["nombre"],
        "apellido": datos_paciente["apellido"],
        "categoria": categoria,
        "descripcion_categoria": desc_categoria,
        "motivo": motivo,
        "hora_llegada": hora_llegada,
    }

    st.session_state["fila_espera"].append(atencion)
    return atencion


# ---------------------------------------------------------
# Vista kiosko
# ---------------------------------------------------------

def vista_kiosko():
    st.title("🏥 Kiosko de Triage (Simulación)")
    st.write("Prototipo académico de una máquina de auto-atención.")

    st.markdown("### 1️⃣ Identificación del paciente")

    rut = st.text_input("RUT (formato chileno)", help="Ejemplo: 11.111.111-1")

    col_buscar, col_limpiar = st.columns(2)
    with col_buscar:
        if st.button("Buscar paciente"):
            if rut in st.session_state["pacientes"]:
                st.success("Paciente encontrado.")
                st.session_state["rut_actual"] = rut
                st.session_state["paciente_actual"] = st.session_state["pacientes"][rut]
            else:
                st.warning("Paciente no encontrado. Complete los datos.")
                st.session_state["rut_actual"] = rut
                st.session_state["paciente_actual"] = None

    with col_limpiar:
        if st.button("Limpiar selección"):
            st.session_state["rut_actual"] = None
            st.session_state["paciente_actual"] = None

    st.markdown("---")
    st.subheader("Datos personales")

    if st.session_state["paciente_actual"]:
        datos = st.session_state["paciente_actual"]
        nombre = st.text_input("Nombre", value=datos["nombre"])
        apellido = st.text_input("Apellido", value=datos["apellido"])
        fecha_nac = st.date_input(
            "Fecha de nacimiento",
            value=datetime.strptime(datos["fecha_nacimiento"], "%Y-%m-%d").date()
        )
    else:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        fecha_nac = st.date_input("Fecha de nacimiento", value=date(2000, 1, 1))

    st.markdown("---")
    st.subheader("2️⃣ Motivo de consulta y signos vitales")

    motivo = st.text_area("Motivo de la consulta (breve descripción)")

    col_temp, col_fc = st.columns(2)
    with col_temp:
        temp = st.number_input("Temperatura (°C)", 30.0, 45.0, 37.0, 0.1)
    with col_fc:
        fc = st.number_input("Frecuencia cardiaca (lat/min)", 30, 200, 80)

    col_pa, col_spo2 = st.columns(2)
    with col_pa:
        pas = st.number_input("Presión sistólica (mmHg)", 50, 250, 120)
        pad = st.number_input("Presión diastólica (mmHg)", 30, 150, 80)
    with col_spo2:
        spo2 = st.number_input("Saturación de oxígeno (%)", 50, 100, 98)

    dolor = st.slider("Nivel de dolor (0 = nada, 10 = máximo)", 0, 10, 3)

    st.markdown("---")
    st.subheader("3️⃣ Generar ticket y prioridad")

    if st.button("Obtener prioridad y ticket"):
        if not rut:
            st.error("Ingresa un RUT.")
            return
        if not nombre or not apellido:
            st.error("Completa los datos personales.")
            return

        registrar_paciente(rut, nombre, apellido, fecha_nac)
        categoria, desc = clasificar_triage(temp, pas, pad, fc, spo2, dolor)
        atencion = agregar_a_fila(rut, categoria, desc, motivo)

        st.success("Paciente registrado en la fila de espera.")
        st.markdown("#### 🎟️ Ticket de atención")
        st.write(f"**Ticket:** {atencion['ticket']}")
        st.write(f"**Paciente:** {atencion['nombre']} {atencion['apellido']} ({rut})")
        st.write(f"**Prioridad:** {atencion['categoria']}")
        st.write(f"**Descripción:** {atencion['descripcion_categoria']}")
        st.info("Diríjase a la sala de espera. Simulación académica.")


# ---------------------------------------------------------
# Vista panel hospital
# ---------------------------------------------------------

def vista_hospital():
    st.title("👨‍⚕️ Panel de Fila de Espera")
    st.write("Vista para el personal del hospital (simulación).")

    fila = st.session_state["fila_espera"]

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


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Simulación Kiosko de Triage",
        page_icon="🏥",
        layout="centered"
    )

    init_state()

    st.sidebar.title("Navegación")
    modo = st.sidebar.radio(
        "Selecciona el modo:",
        ("Kiosko paciente", "Vista hospital")
    )

    if modo == "Kiosko paciente":
        vista_kiosko()
    else:
        vista_hospital()


if __name__ == "__main__":
    main()
