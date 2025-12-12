import streamlit as st
from datetime import datetime, date
import random
import time

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
    # Valores por defecto para signos vitales (usar solo una vez)
    if "k_temp" not in st.session_state:
        st.session_state["k_temp"] = 37.0
    if "k_fc" not in st.session_state:
        st.session_state["k_fc"] = 80
    if "k_pas" not in st.session_state:
        st.session_state["k_pas"] = 120
    if "k_pad" not in st.session_state:
        st.session_state["k_pad"] = 80
    if "k_spo2" not in st.session_state:
        st.session_state["k_spo2"] = 98
    if "k_dolor" not in st.session_state:
        st.session_state["k_dolor"] = 3
    # Estado de la máquina de medición
    if "machine_state" not in st.session_state:
        st.session_state["machine_state"] = "IDLE"  # IDLE | MEASURING | DONE
    if "k_last_measure" not in st.session_state:
        st.session_state["k_last_measure"] = None


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
    # Guardar último ticket generado para mostrar en resumen/ticket
    st.session_state["ultimo_ticket"] = atencion
    return atencion


# ---------------------------------------------------------
# Callbacks
# ---------------------------------------------------------
def simular_signos():
    # callback seguro para actualizar solo los keys k_*
    st.session_state["k_temp"] = round(random.uniform(35.5, 40.0), 1)
    st.session_state["k_fc"] = random.randint(60, 130)
    st.session_state["k_pas"] = random.randint(90, 160)
    st.session_state["k_pad"] = random.randint(60, 100)
    st.session_state["k_spo2"] = random.randint(88, 100)
    st.session_state["k_dolor"] = random.randint(0, 10)
    # registrar hora de la última medición automática
    st.session_state["k_last_measure"] = datetime.now().strftime("%H:%M:%S")


def medir_con_escaneo():
    # Callback que simula una medición secuencial con spinners.
    st.session_state["machine_state"] = "MEASURING"

    with st.spinner("🌡️ Midiendo temperatura..."):
        time.sleep(1.3)
        st.session_state["k_temp"] = round(random.uniform(36.0, 39.6), 1)

    with st.spinner("💓 Midiendo frecuencia cardiaca..."):
        time.sleep(1.3)
        st.session_state["k_fc"] = random.randint(60, 125)

    with st.spinner("🩸 Midiendo presión arterial..."):
        time.sleep(1.8)
        st.session_state["k_pas"] = random.randint(90, 165)
        st.session_state["k_pad"] = random.randint(60, 105)

    with st.spinner("🫁 Midiendo saturación de oxígeno..."):
        time.sleep(1.2)
        st.session_state["k_spo2"] = random.randint(90, 100)

    with st.spinner("🧠 Registrando nivel de dolor..."):
        time.sleep(0.9)
        st.session_state["k_dolor"] = random.randint(0, 10)

    st.session_state["k_last_measure"] = datetime.now().strftime("%H:%M:%S")
    st.session_state["machine_state"] = "DONE"


def reset_medicion():
    st.session_state["machine_state"] = "IDLE"
    st.session_state["k_last_measure"] = None


def buscar_paciente_callback():
    rut_val = st.session_state.get("k_rut", "")
    if rut_val in st.session_state["pacientes"]:
        st.session_state["rut_actual"] = rut_val
        st.session_state["paciente_actual"] = st.session_state["pacientes"][rut_val]
        st.session_state["k_nombre"] = st.session_state["paciente_actual"]["nombre"]
        st.session_state["k_apellido"] = st.session_state["paciente_actual"]["apellido"]
        st.session_state["k_fecha_nac"] = datetime.strptime(st.session_state["paciente_actual"]["fecha_nacimiento"], "%Y-%m-%d").date()
        st.session_state["k_buscar_status"] = "found"
    else:
        st.session_state["rut_actual"] = rut_val
        st.session_state["paciente_actual"] = None
        st.session_state["k_buscar_status"] = "not_found"


def limpiar_seleccion_callback():
    st.session_state["rut_actual"] = None
    st.session_state["paciente_actual"] = None
    st.session_state["k_rut"] = ""
    st.session_state["k_nombre"] = ""
    st.session_state["k_apellido"] = ""
    st.session_state["k_fecha_nac"] = date(2000, 1, 1)
    st.session_state["k_buscar_status"] = None


# ---------------------------------------------------------
# Vista kiosko
# ---------------------------------------------------------

def vista_kiosko():
    # CSS para estilo tipo tarjeta y componentes del kiosko
    st.markdown(
        """
        <style>
        /* Ocultar elementos de Streamlit para apariencia tipo kiosko */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .kiosk-hero { padding: 18px; border-radius: 10px; background: linear-gradient(90deg, rgba(46,134,171,0.08), rgba(46,134,171,0.03)); margin-bottom: 16px; }
        .kiosk-card { padding: 16px; border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; background: rgba(255,255,255,0.92); margin-bottom: 16px; box-shadow: 0 6px 18px rgba(0,0,0,0.03); }
        .kiosk-title { font-size:30px; font-weight:800; margin-bottom:6px; color:#114B5F; }
        .kiosk-disclaimer { font-size:12px; color:#6c757d; }
        .ticket { border:2px dashed #2E86AB; padding:14px; background:#F7FEFF; border-radius:10px; }
        .small-muted { color:#6c757d; font-size:12px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="kiosk-hero"><div class="kiosk-title">🏥 Kiosko de Triage (Simulación)</div><div class="kiosk-disclaimer">Prototipo académico. No usar para decisiones médicas reales.</div></div>', unsafe_allow_html=True)

    # Progreso (3 pasos): identificación, datos personales, ticket
    step = 0
    if st.session_state.get("k_rut"):
        step = 1
    if st.session_state.get("k_nombre") and st.session_state.get("k_apellido"):
        step = 2
    if st.session_state.get("ultimo_ticket"):
        step = 3

    percent = int((step / 3) * 100)
    st.progress(percent)
    st.caption(f"Paso {max(1, step)} de 3…")

    left_col, right_col = st.columns([2, 1], gap="large")

    # --- Columna izquierda: Formularios en tarjetas
    with left_col:
        # Tarjeta 1: Identificación
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.subheader("1️⃣ Identificación del paciente")

        is_measuring = st.session_state.get("machine_state") == "MEASURING"

        rut = st.text_input("RUT (formato chileno)", value=st.session_state.get("k_rut", ""), key="k_rut", help="Ejemplo: 11.111.111-1", disabled=is_measuring)

        col_buscar, col_limpiar = st.columns(2)
        with col_buscar:
            st.button("Buscar paciente", on_click=buscar_paciente_callback, use_container_width=True, disabled=is_measuring)
            # Mostrar estado del último buscar
            status = st.session_state.get("k_buscar_status")
            if status == "found":
                st.success("Paciente encontrado.")
            elif status == "not_found":
                st.warning("Paciente no encontrado. Complete los datos.")

        with col_limpiar:
            st.button("Limpiar selección", on_click=limpiar_seleccion_callback, use_container_width=True, disabled=is_measuring)

        st.markdown('</div>', unsafe_allow_html=True)

        # Tarjeta 2: Datos personales
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.subheader("Datos personales")

        nombre_default = st.session_state.get("k_nombre", "")
        apellido_default = st.session_state.get("k_apellido", "")
        if st.session_state.get("paciente_actual") and not nombre_default:
            nombre_default = st.session_state["paciente_actual"]["nombre"]
            apellido_default = st.session_state["paciente_actual"]["apellido"]

        nombre = st.text_input("Nombre", value=nombre_default, key="k_nombre", disabled=is_measuring)
        apellido = st.text_input("Apellido", value=apellido_default, key="k_apellido", disabled=is_measuring)

        fecha_default = st.session_state.get("k_fecha_nac", date(2000, 1, 1))
        if st.session_state.get("paciente_actual") and not st.session_state.get("k_fecha_nac"):
            fecha_default = datetime.strptime(st.session_state["paciente_actual"]["fecha_nacimiento"], "%Y-%m-%d").date()

        fecha_nac = st.date_input("Fecha de nacimiento", value=fecha_default, key="k_fecha_nac", disabled=is_measuring)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tarjeta 3: Motivo y signos vitales
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.subheader("2️⃣ Motivo de consulta y signos vitales")

        motivo = st.text_area("Motivo de la consulta (breve descripción)", key="k_motivo")

        col_temp, col_fc = st.columns(2)
        with col_temp:
            st.number_input("Temperatura (°C)", 30.0, 45.0, value=st.session_state.get("k_temp", 37.0), step=0.1, key="k_temp", disabled=is_measuring)
        with col_fc:
            st.number_input("Frecuencia cardiaca (lat/min)", 30, 200, value=st.session_state.get("k_fc", 80), key="k_fc", disabled=is_measuring)

        col_pa, col_spo2 = st.columns(2)
        with col_pa:
            st.number_input("Presión sistólica (mmHg)", 50, 250, value=st.session_state.get("k_pas", 120), key="k_pas", disabled=is_measuring)
            st.number_input("Presión diastólica (mmHg)", 30, 150, value=st.session_state.get("k_pad", 80), key="k_pad", disabled=is_measuring)
        with col_spo2:
            st.number_input("Saturación de oxígeno (%)", 50, 100, value=st.session_state.get("k_spo2", 98), key="k_spo2", disabled=is_measuring)

        st.slider("Nivel de dolor (0 = nada, 10 = máximo)", 0, 10, value=st.session_state.get("k_dolor", 3), key="k_dolor", disabled=is_measuring)

        # Botón para iniciar medición automática con escaneo (usa callback)
        st.button("🩺 Iniciar medición automática", on_click=medir_con_escaneo, use_container_width=True, disabled=is_measuring)

        # Mensajes según estado de la máquina y última medición
        state = st.session_state.get("machine_state", "IDLE")
        if state == "MEASURING":
            st.warning("⏳ Manténgase inmóvil mientras se realiza la medición.")
        elif state == "DONE":
            last = st.session_state.get("k_last_measure")
            if last:
                st.success(f"✅ Medición finalizada. Última medición: {last}")
            st.button("🔁 Nueva medición", on_click=reset_medicion, use_container_width=True, disabled=is_measuring)

        st.markdown('</div>', unsafe_allow_html=True)

        # Acción: Generar ticket y prioridad
        st.markdown('')
        rut_val = st.session_state.get("k_rut", "").strip()
        nombre_val = st.session_state.get("k_nombre", "").strip()
        apellido_val = st.session_state.get("k_apellido", "").strip()
        fecha_val = st.session_state.get("k_fecha_nac", date(2000, 1, 1))

        # disabled si falta RUT o datos personales
        generate_disabled = not (rut_val and nombre_val and apellido_val)
        if generate_disabled:
            st.info("Completa: RUT válido → datos personales → signos vitales.")

        if st.button("Obtener prioridad y ticket", use_container_width=True, disabled=generate_disabled):
            registrar_paciente(rut_val, nombre_val, apellido_val, fecha_val)
            # Leer signos vitales desde session_state (no escribir k_* aquí)
            temp = float(st.session_state.get("k_temp", 37.0))
            pas = int(st.session_state.get("k_pas", 120))
            pad = int(st.session_state.get("k_pad", 80))
            fc = int(st.session_state.get("k_fc", 80))
            spo2 = int(st.session_state.get("k_spo2", 98))
            dolor = int(st.session_state.get("k_dolor", 3))

            categoria, desc = clasificar_triage(temp, pas, pad, fc, spo2, dolor)
            atencion = agregar_a_fila(rut_val, categoria, desc, st.session_state.get("k_motivo", ""))
            st.session_state["rut_actual"] = rut_val
            st.session_state["paciente_actual"] = st.session_state["pacientes"][rut_val]
            st.success("Paciente registrado en la fila de espera.")
            st.info("Diríjase a la sala de espera. Simulación académica.")

    # --- Columna derecha: Resumen y ticket
    with right_col:
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.subheader("Resumen")
        rut_show = st.session_state.get("k_rut") or st.session_state.get("rut_actual")
        if rut_show:
            nombre_show = ""
            if st.session_state.get("paciente_actual"):
                p = st.session_state["paciente_actual"]
                nombre_show = f"{p['nombre']} {p['apellido']}"
            elif st.session_state.get("k_nombre") and st.session_state.get("k_apellido"):
                nombre_show = f"{st.session_state.get('k_nombre')} {st.session_state.get('k_apellido')}"

            st.write(f"**RUT:** {rut_show}")
            if nombre_show:
                st.write(f"**Paciente:** {nombre_show}")
        else:
            st.write("-")

        st.markdown('</div>', unsafe_allow_html=True)

        # Mostrar ticket si existe
        if st.session_state.get("ultimo_ticket"):
            t = st.session_state.get("ultimo_ticket")
            ticket_html = f"""
            <div class='ticket'>
            <strong>🎟️ Ticket:</strong> {t['ticket']}<br>
            <strong>Paciente:</strong> {t['nombre']} {t['apellido']} ({t['rut']})<br>
            <strong>Prioridad:</strong> {t['categoria']}<br>
            <strong>Descripción:</strong> {t['descripcion_categoria']}<br>
            <div class='small-muted'>Hora llegada: {t['hora_llegada']}</div>
            </div>
            """
            st.markdown(ticket_html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="small-muted">Aquí aparecerá el ticket luego de generar la prioridad.</div>', unsafe_allow_html=True)



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
        layout="wide"
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
