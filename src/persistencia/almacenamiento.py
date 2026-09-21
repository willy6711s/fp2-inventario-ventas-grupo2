"""Guardado y carga de datos en archivo JSON (HU16)."""

import json
import os

from src.config import ARCHIVO_DATOS
from src.excepciones import ErrorSistema


def guardar(inventario, gestor_ventas, ruta=ARCHIVO_DATOS):
    datos = {
        "inventario": inventario.to_dict(),
        "ventas": gestor_ventas.to_dict(),
    }
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
    except OSError as error:
        raise ErrorSistema(f"No se pudo guardar el archivo: {error}")
    return ruta


def cargar(inventario, gestor_ventas, ruta=ARCHIVO_DATOS):
    if not os.path.exists(ruta):
        raise ErrorSistema(f"No se encontró el archivo de datos: {ruta}")
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, json.JSONDecodeError) as error:
        raise ErrorSistema(f"No se pudo leer el archivo de datos: {error}")
    inventario.cargar_desde_dict(datos.get("inventario", {}))
    gestor_ventas.cargar_desde_dict(datos.get("ventas", {}))
    return inventario, gestor_ventas
