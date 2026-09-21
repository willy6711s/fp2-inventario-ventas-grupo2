"""Jerarquía Repuesto -> RepuestoIndividual / KitRepuestos.

Muestra herencia (atributos y stock comunes) y polimorfismo: cada tipo de
repuesto redefine `precio_unitario()` y `detalle()`.
"""

from abc import ABC, abstractmethod

from src.config import DESCUENTO_KIT
from src.excepciones import DatoInvalidoError, StockInsuficienteError
from src.utils.validaciones import (
    validar_codigo,
    validar_decimal,
    validar_entero,
    validar_texto,
)


class Repuesto(ABC):
    """Clase base de todo artículo del catálogo."""

    def __init__(self, codigo, nombre, marca, categoria, precio_compra,
                 precio_venta, stock=0, stock_minimo=0, proveedor_codigo=None):
        self.codigo = validar_codigo(codigo)
        self.nombre = validar_texto(nombre, "nombre", minimo=3)
        self.marca = validar_texto(marca, "marca", minimo=2)
        self.categoria = validar_texto(categoria, "categoría", minimo=3)
        self.precio_compra = validar_decimal(precio_compra, "precio de compra", 0.01)
        self.precio_venta = validar_decimal(precio_venta, "precio de venta", 0.01)
        if self.precio_venta < self.precio_compra:
            raise DatoInvalidoError(
                "El precio de venta no puede ser menor que el precio de compra."
            )
        self.stock = validar_entero(stock, "stock", 0)
        self.stock_minimo = validar_entero(stock_minimo, "stock mínimo", 0)
        self.proveedor_codigo = (
            validar_codigo(proveedor_codigo) if proveedor_codigo else None
        )
        self.activo = True

    # ---------- métodos abstractos (polimorfismo) ----------
    @property
    @abstractmethod
    def tipo(self):
        """Etiqueta del tipo de repuesto."""

    @abstractmethod
    def precio_unitario(self):
        """Precio de venta efectivo de una unidad."""

    @abstractmethod
    def detalle(self):
        """Descripción ampliada del artículo."""

    # ---------- comportamiento común ----------
    def necesita_reposicion(self):
        """HU10: el stock llegó al mínimo o por debajo."""
        return self.stock <= self.stock_minimo

    def descontar_stock(self, cantidad):
        cantidad = validar_entero(cantidad, "cantidad", 1)
        if cantidad > self.stock:
            raise StockInsuficienteError(self.codigo, cantidad, self.stock)
        self.stock -= cantidad
        return self.stock

    def aumentar_stock(self, cantidad):
        cantidad = validar_entero(cantidad, "cantidad", 1)
        self.stock += cantidad
        return self.stock

    def ajustar_stock(self, nuevo_stock):
        """HU09: ajuste tras conteo físico."""
        self.stock = validar_entero(nuevo_stock, "stock", 0)
        return self.stock

    def hay_disponibilidad(self, cantidad):
        return self.stock >= cantidad

    def valorizacion(self):
        """HU13: stock x costo."""
        return round(self.stock * self.precio_compra, 2)

    def margen_unitario(self):
        return round(self.precio_unitario() - self.precio_compra, 2)

    def dar_de_baja(self):
        self.activo = False

    def __str__(self):
        return (
            f"{self.codigo} | {self.nombre} | {self.tipo} | "
            f"Stock: {self.stock} | S/ {self.precio_unitario():.2f}"
        )

    def to_dict(self):
        return {
            "clase": type(self).__name__,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "marca": self.marca,
            "categoria": self.categoria,
            "precio_compra": self.precio_compra,
            "precio_venta": self.precio_venta,
            "stock": self.stock,
            "stock_minimo": self.stock_minimo,
            "proveedor_codigo": self.proveedor_codigo,
            "activo": self.activo,
        }


class RepuestoIndividual(Repuesto):
    """Pieza suelta: filtro, sello, manguera, etc."""

    def __init__(self, codigo, nombre, marca, categoria, precio_compra,
                 precio_venta, stock=0, stock_minimo=0, proveedor_codigo=None,
                 numero_parte=None):
        super().__init__(codigo, nombre, marca, categoria, precio_compra,
                         precio_venta, stock, stock_minimo, proveedor_codigo)
        self.numero_parte = (numero_parte or self.codigo).strip().upper()

    @property
    def tipo(self):
        return "Individual"

    def precio_unitario(self):
        return self.precio_venta

    def detalle(self):
        return (
            f"Repuesto individual {self.nombre} ({self.marca}) - "
            f"N.° de parte {self.numero_parte}"
        )

    def to_dict(self):
        datos = super().to_dict()
        datos["numero_parte"] = self.numero_parte
        return datos

    @classmethod
    def from_dict(cls, datos):
        repuesto = cls(
            datos["codigo"], datos["nombre"], datos["marca"], datos["categoria"],
            datos["precio_compra"], datos["precio_venta"], datos.get("stock", 0),
            datos.get("stock_minimo", 0), datos.get("proveedor_codigo"),
            datos.get("numero_parte"),
        )
        repuesto.activo = datos.get("activo", True)
        return repuesto


class KitRepuestos(Repuesto):
    """Conjunto de repuestos (por ejemplo, kit de mantenimiento de 500 h).

    Redefine `precio_unitario()`: el precio sale de la suma de sus componentes
    menos el descuento de kit. Si aún no tiene componentes, usa su precio base.
    """

    def __init__(self, codigo, nombre, marca, categoria, precio_compra,
                 precio_venta, stock=0, stock_minimo=0, proveedor_codigo=None,
                 horas_servicio=0, descuento_kit=DESCUENTO_KIT):
        super().__init__(codigo, nombre, marca, categoria, precio_compra,
                         precio_venta, stock, stock_minimo, proveedor_codigo)
        self.horas_servicio = validar_entero(horas_servicio, "horas de servicio", 0)
        self.descuento_kit = validar_decimal(descuento_kit, "descuento del kit", 0.0, 0.5)
        self.componentes = []  # lista de (Repuesto, cantidad)

    def agregar_componente(self, repuesto, cantidad=1):
        if not isinstance(repuesto, Repuesto):
            raise DatoInvalidoError("El componente debe ser un repuesto válido.")
        if repuesto.codigo == self.codigo:
            raise DatoInvalidoError("Un kit no puede contenerse a sí mismo.")
        cantidad = validar_entero(cantidad, "cantidad", 1)
        self.componentes.append((repuesto, cantidad))
        return self.componentes

    @property
    def tipo(self):
        return "Kit"

    def precio_componentes(self):
        return round(
            sum(r.precio_unitario() * c for r, c in self.componentes), 2
        )

    def precio_unitario(self):
        if not self.componentes:
            return self.precio_venta
        return round(self.precio_componentes() * (1 - self.descuento_kit), 2)

    def detalle(self):
        if not self.componentes:
            return f"Kit {self.nombre} (sin componentes registrados)"
        piezas = ", ".join(f"{c} x {r.nombre}" for r, c in self.componentes)
        return f"Kit {self.nombre} ({self.horas_servicio} h): {piezas}"

    def to_dict(self):
        datos = super().to_dict()
        datos["horas_servicio"] = self.horas_servicio
        datos["descuento_kit"] = self.descuento_kit
        datos["componentes"] = [
            {"codigo": r.codigo, "cantidad": c} for r, c in self.componentes
        ]
        return datos

    @classmethod
    def from_dict(cls, datos):
        kit = cls(
            datos["codigo"], datos["nombre"], datos["marca"], datos["categoria"],
            datos["precio_compra"], datos["precio_venta"], datos.get("stock", 0),
            datos.get("stock_minimo", 0), datos.get("proveedor_codigo"),
            datos.get("horas_servicio", 0), datos.get("descuento_kit", DESCUENTO_KIT),
        )
        kit.activo = datos.get("activo", True)
        return kit
