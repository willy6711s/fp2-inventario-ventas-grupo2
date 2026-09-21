"""Jerarquía Documento -> Cotizacion / Comprobante (Factura, Boleta).

Cada documento calcula igual el subtotal, pero redefine su serie, su encabezado
y su emisión: ese es el polimorfismo pedido en el informe.
"""

from abc import ABC, abstractmethod
from datetime import date, timedelta

from src.config import (
    DIAS_VALIDEZ_COTIZACION,
    IGV,
    MONEDA,
    TASA_DESCUENTO,
    UMBRAL_DESCUENTO,
)
from src.excepciones import (
    CotizacionVencidaError,
    DatoInvalidoError,
    OperacionNoPermitidaError,
    StockInsuficienteError,
)
from src.modelos.persona import Cliente, Vendedor
from src.modelos.repuesto import Repuesto
from src.utils.validaciones import validar_entero

ANCHO = 68


class LineaDetalle:
    """Una línea del documento: repuesto, cantidad y precio unitario."""

    def __init__(self, repuesto, cantidad, precio_unitario=None):
        if not isinstance(repuesto, Repuesto):
            raise DatoInvalidoError("La línea debe referirse a un repuesto válido.")
        self.repuesto = repuesto
        self.cantidad = validar_entero(cantidad, "cantidad", 1)
        self.precio_unitario = (
            repuesto.precio_unitario() if precio_unitario is None
            else round(float(precio_unitario), 2)
        )

    @property
    def subtotal(self):
        return round(self.cantidad * self.precio_unitario, 2)

    @property
    def costo(self):
        return round(self.cantidad * self.repuesto.precio_compra, 2)

    def __str__(self):
        return (
            f"{self.repuesto.codigo:<10} {self.repuesto.nombre[:30]:<30} "
            f"{self.cantidad:>5} {self.precio_unitario:>9.2f} {self.subtotal:>10.2f}"
        )

    def to_dict(self):
        return {
            "codigo": self.repuesto.codigo,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
        }


class Documento(ABC):
    """Base común de cotizaciones y comprobantes."""

    def __init__(self, numero, cliente, vendedor, fecha=None):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El documento requiere un cliente válido.")
        if not isinstance(vendedor, Vendedor):
            raise DatoInvalidoError("El documento requiere un vendedor válido.")
        self.numero = int(numero)
        self.cliente = cliente
        self.vendedor = vendedor
        self.fecha = fecha or date.today()
        self.detalles = []

    # ---------- métodos abstractos ----------
    @property
    @abstractmethod
    def serie(self):
        """Prefijo del documento (COT, FAC, BOL)."""

    @property
    @abstractmethod
    def titulo(self):
        """Título que se imprime en la cabecera."""

    @abstractmethod
    def pie(self):
        """Texto final propio de cada documento."""

    # ---------- comportamiento común ----------
    @property
    def codigo(self):
        return f"{self.serie}-{self.numero:06d}"

    def agregar_linea(self, repuesto, cantidad):
        cantidad = validar_entero(cantidad, "cantidad", 1)
        if not repuesto.activo:
            raise OperacionNoPermitidaError(
                f"El repuesto {repuesto.codigo} está dado de baja."
            )
        if not repuesto.hay_disponibilidad(cantidad):
            raise StockInsuficienteError(repuesto.codigo, cantidad, repuesto.stock)
        for linea in self.detalles:
            if linea.repuesto.codigo == repuesto.codigo:
                nueva = linea.cantidad + cantidad
                if not repuesto.hay_disponibilidad(nueva):
                    raise StockInsuficienteError(repuesto.codigo, nueva, repuesto.stock)
                linea.cantidad = nueva
                return linea
        linea = LineaDetalle(repuesto, cantidad)
        self.detalles.append(linea)
        return linea

    @property
    def subtotal(self):
        return round(sum(l.subtotal for l in self.detalles), 2)

    @property
    def descuento(self):
        """HU07: descuento por volumen sobre el subtotal."""
        if self.subtotal > UMBRAL_DESCUENTO:
            return round(self.subtotal * TASA_DESCUENTO, 2)
        return 0.00

    @property
    def base_imponible(self):
        return round(self.subtotal - self.descuento, 2)

    @property
    def igv(self):
        return round(self.base_imponible * IGV, 2)

    @property
    def total(self):
        return round(self.base_imponible + self.igv, 2)

    @property
    def costo_total(self):
        return round(sum(l.costo for l in self.detalles), 2)

    @property
    def utilidad(self):
        """HU14: utilidad bruta = venta neta - costo."""
        return round(self.base_imponible - self.costo_total, 2)

    def emitir(self):
        """Arma el documento en texto. Polimórfico por el título y el pie."""
        if not self.detalles:
            raise OperacionNoPermitidaError(
                "No se puede emitir un documento sin repuestos."
            )
        lineas = []
        lineas.append("=" * ANCHO)
        lineas.append(self.titulo.center(ANCHO))
        lineas.append("=" * ANCHO)
        lineas.append(f" {self.codigo}        Fecha: {self.fecha.strftime('%d/%m/%Y')}")
        lineas.append(
            f" Cliente: {self.cliente.nombre} "
            f"({self.cliente.tipo_documento} {self.cliente.documento})"
        )
        lineas.append(f" Vendedor: {self.vendedor.codigo} - {self.vendedor.nombre}")
        lineas.append("-" * ANCHO)
        lineas.append(
            f"{'Código':<10} {'Repuesto':<30} {'Cant.':>5} {'P.Unit.':>9} {'Subtotal':>10}"
        )
        for linea in self.detalles:
            lineas.append(str(linea))
        lineas.append("-" * ANCHO)
        lineas.append(f"{'Subtotal':<45} {MONEDA} {self.subtotal:>14,.2f}")
        lineas.append(
            f"{'Descuento por volumen (' + str(int(TASA_DESCUENTO * 100)) + ' %)':<45} "
            f"{MONEDA} {self.descuento:>14,.2f}"
        )
        lineas.append(f"{'Base imponible':<45} {MONEDA} {self.base_imponible:>14,.2f}")
        lineas.append(
            f"{'IGV (' + str(int(IGV * 100)) + ' %)':<45} {MONEDA} {self.igv:>14,.2f}"
        )
        lineas.append(f"{'TOTAL':<45} {MONEDA} {self.total:>14,.2f}")
        lineas.append("-" * ANCHO)
        lineas.append(self.pie())
        return "\n".join(lineas)

    def __str__(self):
        return (
            f"{self.codigo} | {self.fecha.strftime('%d/%m/%Y')} | "
            f"{self.cliente.nombre[:25]:<25} | {MONEDA} {self.total:>10,.2f}"
        )

    def to_dict(self):
        return {
            "clase": type(self).__name__,
            "numero": self.numero,
            "fecha": self.fecha.isoformat(),
            "cliente": self.cliente.codigo,
            "vendedor": self.vendedor.codigo,
            "detalles": [l.to_dict() for l in self.detalles],
        }


class Cotizacion(Documento):
    """HU06, HU07, HU11: propuesta con validez limitada."""

    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    FACTURADA = "FACTURADA"

    def __init__(self, numero, cliente, vendedor, fecha=None,
                 dias_validez=DIAS_VALIDEZ_COTIZACION):
        super().__init__(numero, cliente, vendedor, fecha)
        self.dias_validez = validar_entero(dias_validez, "días de validez", 1)
        self.estado = self.PENDIENTE

    @property
    def serie(self):
        return "COT"

    @property
    def titulo(self):
        return "COTIZACIÓN DE REPUESTOS - FERREYROS S.A."

    @property
    def fecha_vencimiento(self):
        return self.fecha + timedelta(days=self.dias_validez)

    def dias_para_vencer(self, hoy=None):
        hoy = hoy or date.today()
        return (self.fecha_vencimiento - hoy).days

    def esta_vencida(self, hoy=None):
        return self.dias_para_vencer(hoy) < 0

    def aprobar(self, hoy=None):
        if self.estado != self.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"La cotización {self.codigo} ya está {self.estado}."
            )
        if self.esta_vencida(hoy):
            self.estado = self.RECHAZADA
            raise CotizacionVencidaError(
                f"La cotización {self.codigo} venció el "
                f"{self.fecha_vencimiento.strftime('%d/%m/%Y')}."
            )
        self.estado = self.APROBADA
        return self.estado

    def rechazar(self):
        self.estado = self.RECHAZADA
        return self.estado

    def pie(self):
        return (
            f" >> Cotización {self.codigo} generada. Válida por "
            f"{self.dias_validez} días (hasta el "
            f"{self.fecha_vencimiento.strftime('%d/%m/%Y')}). Estado: {self.estado}."
        )

    def to_dict(self):
        datos = super().to_dict()
        datos["dias_validez"] = self.dias_validez
        datos["estado"] = self.estado
        return datos


class Comprobante(Documento):
    """Base de los comprobantes de pago que sí descuentan stock."""

    def __init__(self, numero, cliente, vendedor, fecha=None, cotizacion_origen=None):
        super().__init__(numero, cliente, vendedor, fecha)
        self.cotizacion_origen = cotizacion_origen
        self.stock_descontado = False

    @classmethod
    def desde_cotizacion(cls, numero, cotizacion, fecha=None):
        comprobante = cls(numero, cotizacion.cliente, cotizacion.vendedor,
                          fecha or date.today(), cotizacion.codigo)
        for linea in cotizacion.detalles:
            comprobante.detalles.append(
                LineaDetalle(linea.repuesto, linea.cantidad, linea.precio_unitario)
            )
        return comprobante

    def descontar_stock(self):
        """Aplica la salida de almacén una sola vez."""
        if self.stock_descontado:
            raise OperacionNoPermitidaError(
                f"El stock del documento {self.codigo} ya fue descontado."
            )
        for linea in self.detalles:
            if not linea.repuesto.hay_disponibilidad(linea.cantidad):
                raise StockInsuficienteError(
                    linea.repuesto.codigo, linea.cantidad, linea.repuesto.stock
                )
        for linea in self.detalles:
            linea.repuesto.descontar_stock(linea.cantidad)
        self.stock_descontado = True
        return True

    def to_dict(self):
        datos = super().to_dict()
        datos["cotizacion_origen"] = self.cotizacion_origen
        datos["stock_descontado"] = self.stock_descontado
        return datos


class Factura(Comprobante):
    """Se emite a clientes con RUC."""

    def __init__(self, numero, cliente, vendedor, fecha=None, cotizacion_origen=None):
        if not cliente.es_empresa:
            raise OperacionNoPermitidaError(
                "Solo se emite factura a clientes con RUC. Use una boleta."
            )
        super().__init__(numero, cliente, vendedor, fecha, cotizacion_origen)

    @property
    def serie(self):
        return "FAC"

    @property
    def titulo(self):
        return "FACTURA ELECTRÓNICA - FERREYROS S.A."

    def pie(self):
        return (
            f" >> Factura {self.codigo} emitida a RUC {self.cliente.documento}. "
            "Stock actualizado."
        )


class Boleta(Comprobante):
    """Se emite a personas naturales con DNI."""

    @property
    def serie(self):
        return "BOL"

    @property
    def titulo(self):
        return "BOLETA DE VENTA ELECTRÓNICA - FERREYROS S.A."

    def pie(self):
        return (
            f" >> Boleta {self.codigo} emitida a "
            f"{self.cliente.tipo_documento} {self.cliente.documento}. "
            "Stock actualizado."
        )
