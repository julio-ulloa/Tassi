def limpiar_rut(rut: str) -> str:
    return rut.replace(".", "").replace("-", "").strip().upper()

def calcular_dv(cuerpo: str) -> str:
    reversed_digits = list(map(int, reversed(cuerpo)))
    factores = [2, 3, 4, 5, 6, 7]
    suma = 0
    i = 0
    for d in reversed_digits:
        suma += d * factores[i]
        i = (i + 1) % len(factores)
    resto = 11 - (suma % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)

def validar_y_formatear_rut(rut: str):
    rut_limpio = limpiar_rut(rut)
    if len(rut_limpio) < 2:
        return None

    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]

    if not cuerpo.isdigit():
        return None

    dv_correcto = calcular_dv(cuerpo)
    if dv_ingresado != dv_correcto:
        return None

    cuerpo_int = int(cuerpo)
    cuerpo_fmt = f"{cuerpo_int:,}".replace(",", ".")
    return f"{cuerpo_fmt}-{dv_ingresado}"
