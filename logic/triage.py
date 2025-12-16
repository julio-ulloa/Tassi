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
