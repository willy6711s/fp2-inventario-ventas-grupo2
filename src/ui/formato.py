"""Utilidades de presentación para la consola."""

from src.config import MONEDA

ANCHO = 68


def titulo(texto):
    return "\n".join(["=" * ANCHO, texto.upper().center(ANCHO), "=" * ANCHO])


def subtitulo(texto):
    relleno = max(0, ANCHO - len(texto) - 2)
    izq = relleno // 2
    der = relleno - izq
    return f"{'-' * izq} {texto.upper()} {'-' * der}"


def separador(caracter="-"):
    return caracter * ANCHO


def exito(mensaje):
    return f" >> {mensaje}"


def error(mensaje):
    return f" [ERROR] {mensaje}"


def aviso(mensaje):
    return f" [AVISO] {mensaje}"


def soles(monto):
    return f"{MONEDA} {monto:,.2f}"


def tabla_repuestos(repuestos):
    filas = [
        f"{'Código':<10} {'Repuesto':<32} {'Tipo':<11} {'Stock':>6} {'P.Venta':>10}",
        separador(),
    ]
    for r in repuestos:
        filas.append(
            f"{r.codigo:<10} {r.nombre[:32]:<32} {r.tipo:<11} "
            f"{r.stock:>6} {r.precio_unitario():>10,.2f}"
        )
    if not repuestos:
        filas.append(" (sin resultados)")
    return "\n".join(filas)
