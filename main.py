"""Punto de entrada del sistema de inventario y cotizaciones - Ferreyros S.A.

FP2 - Trabajo Parcial (TB1) / Trabajo Final - Grupo 2
Ejecutar con:  python main.py
"""

import sys

from src.excepciones import ErrorSistema
from src.persistencia.datos_demo import cargar_demo
from src.servicios.inventario import Inventario
from src.servicios.ventas import GestorVentas
from src.ui.menu import Aplicacion


def construir_aplicacion(con_demo=True):
    inventario = Inventario()
    ventas = GestorVentas(inventario)
    if con_demo:
        cargar_demo(inventario, ventas)
    return Aplicacion(inventario, ventas)


def main():
    con_demo = "--vacio" not in sys.argv
    app = construir_aplicacion(con_demo)
    if con_demo:
        print(" [AVISO] Se cargaron datos de ejemplo. Use --vacio para iniciar sin datos.")
    try:
        app.menu_principal()
    except KeyboardInterrupt:
        print("\n >> Programa interrumpido por el usuario.")
    except ErrorSistema as error:
        print(f" [ERROR] {error}")


if __name__ == "__main__":
    main()
