import streamlit as st
from datetime import datetime, date
import random

from ui.styles import hero
from logic.rut import validar_y_formatear_rut
from logic.triage import clasificar_triage
from logic.measurement import ensure_measurement_state, medir_con_escaneo, reset_medicion

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

# ---- Callbacks de búsqueda/limpieza (para no tocar keys fuera de callbacks) ----
def buscar_paciente_callback():
    rut_raw = st.session_state.get("k_rut_input", "")
    rut_validado = validar_y_formatear_rut(rut_raw)
    if not rut_validado:
        st.session_state["k_buscar_status"] = ("error", "RUT inválido. Verifica el dígito verificador.")
        return

    rut = rut_validado
    st.session_state["rut_actual"] = rut

    if rut in st.session_state["pacientes"]:
        p = st.session_state["pacientes"][rut]
        st.session_state["paciente_actual"] = p
        st.session_state["k_nombre"] = p["nombre"]
        st.session_state["k_apellido"] = p["apellido"]
        st.session_state["k_fecha_nac"] = datetime.strptime(p["fecha_nacimiento"], "%Y-%m-%d").date()
        st.session_state["k_buscar_status"] = ("ok", f"Paciente encontrado: {rut}")
    else:
        st.session_state["paciente_actual"] = None
        st.session_state["k_buscar_status"] = ("warn", f"Paciente no encontrado. Se registrará como nuevo ({rut}).")

def limpiar_seleccion_callback():
    st.session_state["rut_actual"] = None
    st.session_state["paciente_actual"] = None
    st.session_state["k_rut_input"] = ""
    st.session_state["k_nombre"] = ""
    st.session_state["k_apellido"] = ""
    st.session_state["k_fecha_nac"] = date(2000, 1, 1)
    st.session_state["k_buscar_status"] = None
    reset_medicion()

def render_kiosko():
    ensure_measurement_state()

    hero("🏥 Kiosko de Triage (Simulación)", "Prototipo académico. No usar para decisiones médicas reales.")

    # progreso por pasos (simple)
    st.progress(0.33, text="Paso 1 de 3 — Identificación del paciente")

    col_left, col_right = st.columns([2, 1], gap="large")

    # --- columna derecha: resumen + ticket placeholder
    with col_right:
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.markdown('<div class="kiosk-title">📌 Resumen</div>', unsafe_allow_html=True)
        rut_res = st.session_state.get("rut_actual") or "—"
        nombre_res = (st.session_state.get("k_nombre", "") + " " + st.session_state.get("k_apellido", "")).strip() or "—"
        st.write(f"**RUT:** {rut_res}")
        st.write(f"**Paciente:** {nombre_res}")
        st.markdown('<div class="small-muted">Aquí aparecerá el ticket luego de generar la prioridad.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- identificación
    with col_left:
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.markdown('<div class="kiosk-title">1️⃣ Identificación del paciente</div>', unsafe_allow_html=True)

        if "k_rut_input" not in st.session_state:
            st.session_state["k_rut_input"] = ""
        if "k_buscar_status" not in st.session_state:
            st.session_state["k_buscar_status"] = None

        st.text_input("RUT (formato chileno)", key="k_rut_input", help="Ejemplo: 11.111.111-1")

        b1, b2 = st.columns(2)
        with b1:
            st.button("🔎 Buscar paciente", on_click=buscar_paciente_callback, use_container_width=True)
        with b2:
            st.button("🧹 Limpiar selección", on_click=limpiar_seleccion_callback, use_container_width=True)

        status = st.session_state.get("k_buscar_status")
        if status:
            kind, msg = status
            if kind == "ok":
                st.success(msg)
            elif kind == "warn":
                st.warning(msg)
            else:
                st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)

    # --- datos personales
    with col_left:
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.markdown('<div class="kiosk-title">🧾 Datos personales</div>', unsafe_allow_html=True)

        if "k_nombre" not in st.session_state: st.session_state["k_nombre"] = ""
        if "k_apellido" not in st.session_state: st.session_state["k_apellido"] = ""
        if "k_fecha_nac" not in st.session_state: st.session_state["k_fecha_nac"] = date(2000, 1, 1)

        st.text_input("Nombre", key="k_nombre")
        st.text_input("Apellido", key="k_apellido")
        st.date_input("Fecha de nacimiento", key="k_fecha_nac")

        st.markdown("</div>", unsafe_allow_html=True)

    st.progress(0.66, text="Paso 2 de 3 — Motivo de consulta y signos vitales")

    # --- signos vitales
    is_measuring = st.session_state.get("machine_state") == "MEASURING"

    with col_left:
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.markdown('<div class="kiosk-title">2️⃣ Motivo de consulta y signos vitales</div>', unsafe_allow_html=True)

        motivo = st.text_area("Motivo de la consulta (breve descripción)", key="k_motivo")

        a, b = st.columns(2)
        with a:
            st.number_input("Temperatura (°C)", 30.0, 45.0, step=0.1, key="k_temp", disabled=is_measuring)
            st.number_input("Presión sistólica (mmHg)", 50, 250, key="k_pas", disabled=is_measuring)
            st.number_input("Presión diastólica (mmHg)", 30, 150, key="k_pad", disabled=is_measuring)

        with b:
            st.number_input("Frecuencia cardiaca (lat/min)", 30, 200, key="k_fc", disabled=is_measuring)
            st.number_input("Saturación de oxígeno (%)", 50, 100, key="k_spo2", disabled=is_measuring)
            st.slider("Nivel de dolor (0–10)", 0, 10, key="k_dolor", disabled=is_measuring)

        st.button(
            "🩺 Iniciar medición automática",
            on_click=medir_con_escaneo,
            disabled=is_measuring,
            use_container_width=True
        )

        st.button(
            "🔁 Nueva medición",
            on_click=reset_medicion,
            disabled=is_measuring,
            use_container_width=True
        )

        state = st.session_state.get("machine_state", "IDLE")
        if state == "MEASURING":
            st.warning("⏳ Manténgase inmóvil mientras se realiza la medición.")
        elif state == "DONE":
            last = st.session_state.get("k_last_measure")
            if last:
                st.success(f"✅ Medición finalizada. Última medición: {last}")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- generar ticket
    st.progress(1.0, text="Paso 3 de 3 — Generar ticket y prioridad")

    rut_ok = bool(st.session_state.get("rut_actual"))
    datos_ok = bool(st.session_state.get("k_nombre") and st.session_state.get("k_apellido"))
    puede_generar = rut_ok and datos_ok and not is_measuring

    with col_left:
        st.markdown('<div class="kiosk-card">', unsafe_allow_html=True)
        st.markdown('<div class="kiosk-title">3️⃣ Generar ticket y prioridad</div>', unsafe_allow_html=True)

        if not puede_generar:
            st.info("Completa: RUT válido → datos personales → signos vitales (y espera a que termine la medición).")

        if st.button("🎟️ Obtener prioridad y ticket", use_container_width=True, disabled=not puede_generar):
            rut = st.session_state["rut_actual"]
            nombre = st.session_state["k_nombre"]
            apellido = st.session_state["k_apellido"]
            fecha_nac = st.session_state["k_fecha_nac"]

            registrar_paciente(rut, nombre, apellido, fecha_nac)

            temp = float(st.session_state["k_temp"])
            fc = int(st.session_state["k_fc"])
            pas = int(st.session_state["k_pas"])
            pad = int(st.session_state["k_pad"])
            spo2 = int(st.session_state["k_spo2"])
            dolor = int(st.session_state["k_dolor"])

            categoria, desc = clasificar_triage(temp, pas, pad, fc, spo2, dolor)
            atencion = agregar_a_fila(rut, categoria, desc, st.session_state.get("k_motivo", ""))

            # mostrar ticket en derecha
            with col_right:
                st.markdown('<div class="ticket">', unsafe_allow_html=True)
                st.markdown("### 🎟️ Ticket de atención")
                st.write(f"**Ticket:** {atencion['ticket']}")
                st.write(f"**Paciente:** {atencion['nombre']} {atencion['apellido']}")
                st.write(f"**RUT:** {atencion['rut']}")
                st.write(f"**Prioridad:** {atencion['categoria']}")
                st.write(f"**Detalle:** {atencion['descripcion_categoria']}")
                st.caption("Diríjase a la sala de espera. Simulación académica.")
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
