"""Reportes de gestión: utilidad, comisiones y valorización (HU12, HU13, HU14)."""

from src.config import MONEDA


class GeneradorReportes:
    def __init__(self, inventario, gestor_ventas):
        self.inventario = inventario
        self.ventas = gestor_ventas

    # ---------------- utilidades ----------------
    def _comprobantes_periodo(self, anio=None, mes=None):
        comprobantes = self.ventas.comprobantes
        if anio is not None:
            comprobantes = [c for c in comprobantes if c.fecha.year == anio]
        if mes is not None:
            comprobantes = [c for c in comprobantes if c.fecha.month == mes]
        return comprobantes

    def resumen_periodo(self, anio=None, mes=None):
        """HU14: ventas netas, costo, utilidad bruta y margen."""
        comprobantes = self._comprobantes_periodo(anio, mes)
        ventas_netas = round(sum(c.base_imponible for c in comprobantes), 2)
        costo = round(sum(c.costo_total for c in comprobantes), 2)
        utilidad = round(ventas_netas - costo, 2)
        margen = round(utilidad / ventas_netas * 100, 2) if ventas_netas else 0.0
        return {
            "documentos": len(comprobantes),
            "ventas_netas": ventas_netas,
            "costo_ventas": costo,
            "utilidad_bruta": utilidad,
            "margen_bruto": margen,
            "valorizacion_inventario": self.inventario.valorizacion_total(),
        }

    def comisiones(self, anio=None, mes=None):
        """HU12: comisión por vendedor sobre sus ventas netas del periodo."""
        comprobantes = self._comprobantes_periodo(anio, mes)
        acumulado = {}
        for comprobante in comprobantes:
            codigo = comprobante.vendedor.codigo
            acumulado[codigo] = acumulado.get(codigo, 0) + comprobante.base_imponible
        filas = []
        for vendedor in self.ventas.listar_vendedores():
            ventas = round(acumulado.get(vendedor.codigo, 0), 2)
            filas.append({
                "codigo": vendedor.codigo,
                "nombre": vendedor.nombre,
                "ventas_netas": ventas,
                "comision": vendedor.calcular_comision(ventas),
                "cumplio_meta": vendedor.cumplio_meta(ventas),
            })
        return sorted(filas, key=lambda f: f["ventas_netas"], reverse=True)

    def ranking_repuestos(self, top=5):
        vendidos = {}
        for comprobante in self.ventas.comprobantes:
            for linea in comprobante.detalles:
                clave = linea.repuesto.codigo
                datos = vendidos.setdefault(
                    clave, {"nombre": linea.repuesto.nombre, "cantidad": 0, "monto": 0.0}
                )
                datos["cantidad"] += linea.cantidad
                datos["monto"] = round(datos["monto"] + linea.subtotal, 2)
        filas = [dict(codigo=k, **v) for k, v in vendidos.items()]
        return sorted(filas, key=lambda f: f["monto"], reverse=True)[:top]

    # ---------------- salida en texto ----------------
    def texto_resumen(self, anio=None, mes=None):
        datos = self.resumen_periodo(anio, mes)
        periodo = f"{mes:02d}/{anio}" if (anio and mes) else "TODO EL HISTORIAL"
        lineas = [
            "=" * 68,
            f" REPORTE DEL PERIODO: {periodo}".center(68),
            "=" * 68,
            f" Documentos emitidos ................... {datos['documentos']:>14}",
            f" Ventas netas (sin IGV) ................ {MONEDA} {datos['ventas_netas']:>12,.2f}",
            f" Costo de ventas ....................... {MONEDA} {datos['costo_ventas']:>12,.2f}",
            f" Utilidad bruta ........................ {MONEDA} {datos['utilidad_bruta']:>12,.2f}",
            f" Margen bruto .......................... {datos['margen_bruto']:>13.2f} %",
            f" Valorización del inventario al costo .. {MONEDA} {datos['valorizacion_inventario']:>12,.2f}",
            "-" * 68,
            " COMISIONES SOBRE VENTAS NETAS",
            f" {'Vendedor':<26} {'Ventas netas':>16} {'Comisión':>16}",
        ]
        for fila in self.comisiones(anio, mes):
            lineas.append(
                f" {fila['codigo'] + ' ' + fila['nombre'][:20]:<26} "
                f"{MONEDA + ' ' + format(fila['ventas_netas'], ',.2f'):>16} "
                f"{MONEDA + ' ' + format(fila['comision'], ',.2f'):>16}"
            )
        lineas.append("=" * 68)
        return "\n".join(lineas)
