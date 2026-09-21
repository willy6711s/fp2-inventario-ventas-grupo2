"""Servicio de catálogo y stock (HU01, HU02, HU03, HU04, HU09, HU10, HU13)."""

from datetime import date

from src.excepciones import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)
from src.modelos.movimiento import MovimientoStock
from src.modelos.proveedor import Proveedor
from src.modelos.repuesto import KitRepuestos, Repuesto, RepuestoIndividual
from src.utils.validaciones import validar_entero


class Inventario:
    def __init__(self):
        self._repuestos = {}
        self._proveedores = {}
        self.movimientos = []

    # ---------------- proveedores (HU04) ----------------
    def registrar_proveedor(self, proveedor):
        if not isinstance(proveedor, Proveedor):
            raise OperacionNoPermitidaError("Se esperaba un proveedor.")
        if proveedor.codigo in self._proveedores:
            raise EntidadDuplicadaError(
                f"Ya existe el proveedor {proveedor.codigo}."
            )
        self._proveedores[proveedor.codigo] = proveedor
        return proveedor

    def obtener_proveedor(self, codigo):
        codigo = str(codigo).strip().upper()
        if codigo not in self._proveedores:
            raise EntidadNoEncontradaError(f"No existe el proveedor {codigo}.")
        return self._proveedores[codigo]

    def listar_proveedores(self, solo_activos=True):
        return [
            p for p in self._proveedores.values()
            if p.activo or not solo_activos
        ]

    # ---------------- repuestos (HU01, HU02, HU03) ----------------
    def registrar_repuesto(self, repuesto):
        if not isinstance(repuesto, Repuesto):
            raise OperacionNoPermitidaError("Se esperaba un repuesto o un kit.")
        if repuesto.codigo in self._repuestos:
            raise EntidadDuplicadaError(
                f"Ya existe un repuesto con el código {repuesto.codigo}."
            )
        if repuesto.proveedor_codigo:
            self.obtener_proveedor(repuesto.proveedor_codigo)
        self._repuestos[repuesto.codigo] = repuesto
        if repuesto.stock > 0:
            self.movimientos.append(
                MovimientoStock(repuesto.codigo, "INGRESO", repuesto.stock,
                                "Stock inicial")
            )
        return repuesto

    def obtener_repuesto(self, codigo):
        codigo = str(codigo).strip().upper()
        if codigo not in self._repuestos:
            raise EntidadNoEncontradaError(f"No existe el repuesto {codigo}.")
        return self._repuestos[codigo]

    def buscar(self, texto, por="nombre"):
        """HU02: busca por número de parte/código o por nombre."""
        texto = str(texto).strip().lower()
        resultados = []
        for repuesto in self._repuestos.values():
            if not repuesto.activo:
                continue
            if por == "codigo":
                campo = repuesto.codigo.lower()
                extra = getattr(repuesto, "numero_parte", "").lower()
                if texto in campo or (extra and texto in extra):
                    resultados.append(repuesto)
            else:
                if (texto in repuesto.nombre.lower()
                        or texto in repuesto.categoria.lower()
                        or texto in repuesto.marca.lower()):
                    resultados.append(repuesto)
        return sorted(resultados, key=lambda r: r.codigo)

    def listar_repuestos(self, solo_activos=True):
        return sorted(
            [r for r in self._repuestos.values() if r.activo or not solo_activos],
            key=lambda r: r.codigo,
        )

    def modificar_repuesto(self, codigo, **campos):
        """HU03: modifica precios, stock mínimo, categoría, etc."""
        repuesto = self.obtener_repuesto(codigo)
        permitidos = {
            "nombre", "marca", "categoria", "precio_compra", "precio_venta",
            "stock_minimo", "proveedor_codigo",
        }
        for campo, valor in campos.items():
            if campo not in permitidos:
                raise OperacionNoPermitidaError(
                    f"El campo '{campo}' no se puede modificar."
                )
            setattr(repuesto, campo, valor)
        return repuesto

    def dar_de_baja(self, codigo):
        repuesto = self.obtener_repuesto(codigo)
        repuesto.dar_de_baja()
        return repuesto

    # ---------------- kits ----------------
    def armar_kit(self, codigo_kit, componentes):
        """componentes: lista de tuplas (codigo_repuesto, cantidad)."""
        kit = self.obtener_repuesto(codigo_kit)
        if not isinstance(kit, KitRepuestos):
            raise OperacionNoPermitidaError(f"{codigo_kit} no es un kit.")
        kit.componentes.clear()
        for codigo, cantidad in componentes:
            kit.agregar_componente(self.obtener_repuesto(codigo), cantidad)
        return kit

    # ---------------- movimientos (HU09) ----------------
    def registrar_ingreso(self, codigo, cantidad, motivo="Ingreso de mercadería",
                          documento="", fecha=None):
        repuesto = self.obtener_repuesto(codigo)
        cantidad = validar_entero(cantidad, "cantidad", 1)
        repuesto.aumentar_stock(cantidad)
        movimiento = MovimientoStock(repuesto.codigo, "INGRESO", cantidad, motivo,
                                     fecha or date.today(), documento)
        self.movimientos.append(movimiento)
        return movimiento

    def registrar_salida(self, codigo, cantidad, motivo="Salida por venta",
                         documento="", fecha=None):
        repuesto = self.obtener_repuesto(codigo)
        cantidad = validar_entero(cantidad, "cantidad", 1)
        repuesto.descontar_stock(cantidad)
        movimiento = MovimientoStock(repuesto.codigo, "SALIDA", cantidad, motivo,
                                     fecha or date.today(), documento)
        self.movimientos.append(movimiento)
        return movimiento

    def registrar_ajuste(self, codigo, stock_real, motivo="Ajuste por conteo físico",
                         fecha=None):
        repuesto = self.obtener_repuesto(codigo)
        stock_real = validar_entero(stock_real, "stock real", 0)
        diferencia = stock_real - repuesto.stock
        repuesto.ajustar_stock(stock_real)
        movimiento = MovimientoStock(repuesto.codigo, "AJUSTE", abs(diferencia),
                                     f"{motivo} (dif. {diferencia:+d})",
                                     fecha or date.today())
        self.movimientos.append(movimiento)
        return movimiento

    def historial_movimientos(self, codigo=None):
        if codigo is None:
            return list(self.movimientos)
        codigo = str(codigo).strip().upper()
        return [m for m in self.movimientos if m.codigo_repuesto == codigo]

    # ---------------- reportes de inventario ----------------
    def alertas_stock(self):
        """HU10: repuestos activos con stock igual o menor al mínimo."""
        return sorted(
            [r for r in self._repuestos.values() if r.activo and r.necesita_reposicion()],
            key=lambda r: (r.stock - r.stock_minimo, r.codigo),
        )

    def valorizacion_total(self):
        """HU13: suma de stock x costo de todos los repuestos activos."""
        return round(
            sum(r.valorizacion() for r in self._repuestos.values() if r.activo), 2
        )

    def total_repuestos(self):
        return len([r for r in self._repuestos.values() if r.activo])

    # ---------------- persistencia (HU16) ----------------
    def to_dict(self):
        return {
            "proveedores": [p.to_dict() for p in self._proveedores.values()],
            "repuestos": [r.to_dict() for r in self._repuestos.values()],
            "movimientos": [m.to_dict() for m in self.movimientos],
        }

    def cargar_desde_dict(self, datos):
        for item in datos.get("proveedores", []):
            self._proveedores[item["codigo"]] = Proveedor.from_dict(item)
        pendientes_kits = []
        for item in datos.get("repuestos", []):
            if item.get("clase") == "KitRepuestos":
                kit = KitRepuestos.from_dict(item)
                self._repuestos[kit.codigo] = kit
                pendientes_kits.append((kit, item.get("componentes", [])))
            else:
                repuesto = RepuestoIndividual.from_dict(item)
                self._repuestos[repuesto.codigo] = repuesto
        for kit, componentes in pendientes_kits:
            for comp in componentes:
                try:
                    kit.agregar_componente(
                        self.obtener_repuesto(comp["codigo"]), comp["cantidad"]
                    )
                except EntidadNoEncontradaError:
                    continue
        self.movimientos = [
            MovimientoStock.from_dict(m) for m in datos.get("movimientos", [])
        ]
        return self
