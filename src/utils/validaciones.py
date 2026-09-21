"""Validaciones reutilizables de entrada de datos."""

import re

from src.excepciones import DatoInvalidoError

PATRON_CODIGO = re.compile(r"^[A-Z]{3}-\d{3,4}$")
PATRON_RUC = re.compile(r"^\d{11}$")
PATRON_DNI = re.compile(r"^\d{8}$")
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def validar_texto(valor, campo, minimo=2, maximo=80):
    if valor is None:
        raise DatoInvalidoError(f"El campo '{campo}' es obligatorio.")
    texto = str(valor).strip()
    if len(texto) < minimo:
        raise DatoInvalidoError(
            f"El campo '{campo}' debe tener al menos {minimo} caracteres."
        )
    if len(texto) > maximo:
        raise DatoInvalidoError(
            f"El campo '{campo}' no debe superar los {maximo} caracteres."
        )
    return texto


def validar_entero(valor, campo, minimo=0, maximo=None):
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError):
        raise DatoInvalidoError(f"El campo '{campo}' debe ser un número entero.")
    if numero < minimo:
        raise DatoInvalidoError(f"El campo '{campo}' no puede ser menor que {minimo}.")
    if maximo is not None and numero > maximo:
        raise DatoInvalidoError(f"El campo '{campo}' no puede ser mayor que {maximo}.")
    return numero


def validar_decimal(valor, campo, minimo=0.0, maximo=None):
    try:
        numero = float(str(valor).strip().replace(",", "."))
    except (TypeError, ValueError):
        raise DatoInvalidoError(f"Ingrese un valor numérico válido en '{campo}'.")
    if numero < minimo:
        raise DatoInvalidoError(f"El campo '{campo}' no puede ser menor que {minimo}.")
    if maximo is not None and numero > maximo:
        raise DatoInvalidoError(f"El campo '{campo}' no puede ser mayor que {maximo}.")
    return round(numero, 2)


def validar_codigo(valor, campo="código"):
    codigo = str(valor).strip().upper()
    if not PATRON_CODIGO.match(codigo):
        raise DatoInvalidoError(
            f"El {campo} debe tener el formato XXX-000 (por ejemplo REP-0101)."
        )
    return codigo


def validar_ruc(valor):
    ruc = str(valor).strip()
    if not PATRON_RUC.match(ruc):
        raise DatoInvalidoError("El RUC debe tener 11 dígitos.")
    if ruc[:2] not in ("10", "15", "17", "20"):
        raise DatoInvalidoError("El RUC debe iniciar con 10, 15, 17 o 20.")
    return ruc


def validar_dni(valor):
    dni = str(valor).strip()
    if not PATRON_DNI.match(dni):
        raise DatoInvalidoError("El DNI debe tener 8 dígitos.")
    return dni


def validar_documento_identidad(valor):
    """Acepta RUC (11 dígitos) o DNI (8 dígitos) y devuelve (documento, tipo)."""
    texto = str(valor).strip()
    if len(texto) == 11:
        return validar_ruc(texto), "RUC"
    if len(texto) == 8:
        return validar_dni(texto), "DNI"
    raise DatoInvalidoError("Ingrese un RUC de 11 dígitos o un DNI de 8 dígitos.")


def validar_correo(valor):
    if valor in (None, ""):
        return ""
    correo = str(valor).strip()
    if not PATRON_CORREO.match(correo):
        raise DatoInvalidoError("El correo electrónico no tiene un formato válido.")
    return correo


def validar_telefono(valor):
    if valor in (None, ""):
        return ""
    telefono = str(valor).strip()
    if not re.match(r"^[\d\s\-\+\(\)]{6,20}$", telefono):
        raise DatoInvalidoError("El teléfono solo admite dígitos y de 6 a 20 caracteres.")
    return telefono
