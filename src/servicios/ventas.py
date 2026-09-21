"""Servicio de clientes, vendedores, cotizaciones y ventas (HU05 a HU08, HU11, HU15)."""

from datetime import date

from src.excepciones import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
)
from src.modelos.documento import Boleta, Comprobante, Cotizacion, Factura
from src.modelos.persona import Cliente, Vendedor


class GestorVentas:
    def __init__(self, inventario):
        self.inventario = inventario
        self._clientes = {}
        self._vendedores = {}
        self.cotizaciones = []
        self.comprobantes = []
        self._correlativo_cotizacion = 0
        self._correlativo_comprobante = 0

    # ---------------- clientes y vendedores (HU05) ----------------
    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise OperacionNoPermitidaError("Se esperaba un cliente.")
        if cliente.codigo in self._clientes:
            raise EntidadDuplicadaError(f"Ya existe el cliente {cliente.codigo}.")
        for existente in self._clientes.values():
            if existente.documento == cliente.documento:
                raise EntidadDuplicadaError(
                    f"El documento {cliente.documento} ya está registrado "
                    f"en {existente.codigo}."
                )
        self._clientes[cliente.codigo] = cliente
        return cliente

    def registrar_vendedor(self, vendedor):
        if not isinstance(vendedor, Vendedor):
            raise OperacionNoPermitidaError("Se esperaba un vendedor.")
        if vendedor.codigo in self._vendedores:
            raise EntidadDuplicadaError(f"Ya existe el vendedor {vendedor.codigo}.")
        self._vendedores[vendedor.codigo] = vendedor
        return vendedor

    def obtener_cliente(self, clave):
        clave = str(clave).strip().upper()
        if clave in self._clientes:
            return self._clientes[clave]
        for cliente in self._clientes.values():
            if cliente.documento == clave:
                return cliente
        raise EntidadNoEncontradaError(f"No existe el cliente {clave}.")

    def obtener_vendedor(self, codigo):
        codigo = str(codigo).strip().upper()
        if codigo not in self._vendedores:
            raise EntidadNoEncontradaError(f"No existe el vendedor {codigo}.")
        return self._vendedores[codigo]

    def listar_clientes(self):
        return sorted(self._clientes.values(), key=lambda c: c.codigo)

    def listar_vendedores(self):
        return sorted(self._vendedores.values(), key=lambda v: v.codigo)

    def buscar_clientes(self, texto):
        texto = str(texto).strip().lower()
        return [
            c for c in self._clientes.values()
            if texto in c.nombre.lower() or texto in c.documento
        ]

    # ---------------- cotizaciones (HU06, HU07) ----------------
    def crear_cotizacion(self, codigo_cliente, codigo_vendedor, items, fecha=None):
        """items: lista de tuplas (codigo_repuesto, cantidad)."""
        cliente = self.obtener_cliente(codigo_cliente)
        vendedor = self.obtener_vendedor(codigo_vendedor)
        self._correlativo_cotizacion += 1
        cotizacion = Cotizacion(
            self._correlativo_cotizacion, cliente, vendedor, fecha or date.today()
        )
        try:
            for codigo, cantidad in items:
                repuesto = self.inventario.obtener_repuesto(codigo)
                cotizacion.agregar_linea(repuesto, cantidad)
        except Exception:
            self._correlativo_cotizacion -= 1
            raise
        self.cotizaciones.append(cotizacion)
        return cotizacion

    def obtener_cotizacion(self, codigo):
        codigo = str(codigo).strip().upper()
        for cotizacion in self.cotizaciones:
            if cotizacion.codigo == codigo:
                return cotizacion
        raise EntidadNoEncontradaError(f"No existe la cotización {codigo}.")

    def cotizaciones_pendientes(self, hoy=None):
        hoy = hoy or date.today()
        pendientes = []
        for cotizacion in self.cotizaciones:
            if cotizacion.estado != Cotizacion.PENDIENTE:
                continue
            if cotizacion.esta_vencida(hoy):
                continue
            pendientes.append(cotizacion)
        return sorted(pendientes, key=lambda c: c.fecha_vencimiento)

    def cotizaciones_por_vencer(self, dias=7, hoy=None):
        """HU11: pendientes que vencen dentro de los próximos `dias` días."""
        return [
            c for c in self.cotizaciones_pendientes(hoy)
            if c.dias_para_vencer(hoy) <= dias
        ]

    # ---------------- venta (HU08) ----------------
    def convertir_en_comprobante(self, codigo_cotizacion, fecha=None, hoy=None):
        """Aprueba la cotización, emite factura o boleta y descuenta stock."""
        cotizacion = self.obtener_cotizacion(codigo_cotizacion)
        cotizacion.aprobar(hoy)
        self._correlativo_comprobante += 1
        clase = Factura if cotizacion.cliente.es_empresa else Boleta
        comprobante = clase.desde_cotizacion(
            self._correlativo_comprobante, cotizacion, fecha or date.today()
        )
        try:
            comprobante.descontar_stock()
        except Exception:
            self._correlativo_comprobante -= 1
            cotizacion.estado = Cotizacion.PENDIENTE
            raise
        for linea in comprobante.detalles:
            self.inventario.movimientos.append(
                self._movimiento_salida(linea, comprobante)
            )
        cotizacion.estado = Cotizacion.FACTURADA
        self.comprobantes.append(comprobante)
        return comprobante

    @staticmethod
    def _movimiento_salida(linea, comprobante):
        from src.modelos.movimiento import MovimientoStock
        return MovimientoStock(
            linea.repuesto.codigo, "SALIDA", linea.cantidad,
            f"Venta {comprobante.codigo}", comprobante.fecha, comprobante.codigo
        )

    def venta_directa(self, codigo_cliente, codigo_vendedor, items, fecha=None):
        """Cotización + comprobante en un solo paso."""
        cotizacion = self.crear_cotizacion(codigo_cliente, codigo_vendedor, items, fecha)
        return self.convertir_en_comprobante(cotizacion.codigo, fecha, fecha)

    # ---------------- historial (HU15) ----------------
    def historial(self, desde=None, hasta=None, cliente=None, vendedor=None):
        documentos = list(self.cotizaciones) + list(self.comprobantes)
        if desde:
            documentos = [d for d in documentos if d.fecha >= desde]
        if hasta:
            documentos = [d for d in documentos if d.fecha <= hasta]
        if cliente:
            cliente = str(cliente).upper()
            documentos = [
                d for d in documentos
                if d.cliente.codigo == cliente or d.cliente.documento == cliente
            ]
        if vendedor:
            vendedor = str(vendedor).upper()
            documentos = [d for d in documentos if d.vendedor.codigo == vendedor]
        return sorted(documentos, key=lambda d: (d.fecha, d.codigo))

    # ---------------- persistencia (HU16) ----------------
    def to_dict(self):
        return {
            "clientes": [c.to_dict() for c in self._clientes.values()],
            "vendedores": [v.to_dict() for v in self._vendedores.values()],
            "cotizaciones": [c.to_dict() for c in self.cotizaciones],
            "comprobantes": [c.to_dict() for c in self.comprobantes],
            "correlativo_cotizacion": self._correlativo_cotizacion,
            "correlativo_comprobante": self._correlativo_comprobante,
        }

    def cargar_desde_dict(self, datos):
        for item in datos.get("clientes", []):
            cliente = Cliente.from_dict(item)
            self._clientes[cliente.codigo] = cliente
        for item in datos.get("vendedores", []):
            vendedor = Vendedor.from_dict(item)
            self._vendedores[vendedor.codigo] = vendedor
        for item in datos.get("cotizaciones", []):
            cotizacion = Cotizacion(
                item["numero"],
                self.obtener_cliente(item["cliente"]),
                self.obtener_vendedor(item["vendedor"]),
                date.fromisoformat(item["fecha"]),
                item.get("dias_validez", 15),
            )
            for linea in item.get("detalles", []):
                repuesto = self.inventario.obtener_repuesto(linea["codigo"])
                from src.modelos.documento import LineaDetalle
                cotizacion.detalles.append(
                    LineaDetalle(repuesto, linea["cantidad"], linea["precio_unitario"])
                )
            cotizacion.estado = item.get("estado", Cotizacion.PENDIENTE)
            self.cotizaciones.append(cotizacion)
        for item in datos.get("comprobantes", []):
            clase = Factura if item.get("clase") == "Factura" else Boleta
            comprobante = clase(
                item["numero"],
                self.obtener_cliente(item["cliente"]),
                self.obtener_vendedor(item["vendedor"]),
                date.fromisoformat(item["fecha"]),
                item.get("cotizacion_origen"),
            )
            from src.modelos.documento import LineaDetalle
            for linea in item.get("detalles", []):
                repuesto = self.inventario.obtener_repuesto(linea["codigo"])
                comprobante.detalles.append(
                    LineaDetalle(repuesto, linea["cantidad"], linea["precio_unitario"])
                )
            comprobante.stock_descontado = item.get("stock_descontado", True)
            self.comprobantes.append(comprobante)
        self._correlativo_cotizacion = datos.get(
            "correlativo_cotizacion", len(self.cotizaciones)
        )
        self._correlativo_comprobante = datos.get(
            "correlativo_comprobante", len(self.comprobantes)
        )
        return self
