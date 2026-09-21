"""Pruebas del flujo de venta y de los reportes (HU05-HU08, HU11-HU15)."""

import unittest
from datetime import date, timedelta

from src.excepciones import EntidadDuplicadaError, EntidadNoEncontradaError
from src.modelos.persona import Cliente, Vendedor
from src.modelos.proveedor import Proveedor
from src.modelos.repuesto import RepuestoIndividual
from src.servicios.inventario import Inventario
from src.servicios.reportes import GeneradorReportes
from src.servicios.ventas import GestorVentas


class TestFlujoVenta(unittest.TestCase):
    def setUp(self):
        self.inv = Inventario()
        self.inv.registrar_proveedor(Proveedor("PRV-001", "Caterpillar", "20100055555"))
        self.inv.registrar_repuesto(
            RepuestoIndividual("REP-0101", "Filtro de aceite", "CAT", "Filtros",
                               60, 85, 40, 10, "PRV-001")
        )
        self.inv.registrar_repuesto(
            RepuestoIndividual("REP-0310", "Kit de sellos", "CAT", "Sellos",
                               160, 240, 10, 5, "PRV-001")
        )
        self.ventas = GestorVentas(self.inv)
        self.ventas.registrar_vendedor(
            Vendedor("VEN-002", "Diego Salas", "45667788", tasa_comision=0.02)
        )
        self.ventas.registrar_cliente(
            Cliente("CLI-001", "Minera Ejemplo S.A.C.", "20512345678")
        )
        self.ventas.registrar_cliente(
            Cliente("CLI-004", "Carlos Mendoza", "45123789")
        )
        self.reportes = GeneradorReportes(self.inv, self.ventas)

    def test_no_duplica_documento_de_cliente(self):
        with self.assertRaises(EntidadDuplicadaError):
            self.ventas.registrar_cliente(
                Cliente("CLI-009", "Otra empresa", "20512345678")
            )

    def test_busqueda_de_cliente_por_ruc(self):
        cliente = self.ventas.obtener_cliente("20512345678")
        self.assertEqual(cliente.codigo, "CLI-001")

    def test_cliente_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.ventas.obtener_cliente("CLI-777")

    def test_cotizacion_con_totales_del_informe(self):
        cotizacion = self.ventas.crear_cotizacion(
            "CLI-001", "VEN-002", [("REP-0101", 6), ("REP-0310", 2)]
        )
        self.assertEqual(cotizacion.subtotal, 990.00)
        self.assertEqual(cotizacion.total, 1109.79)

    def test_cotizacion_no_descuenta_stock(self):
        self.ventas.crear_cotizacion("CLI-001", "VEN-002", [("REP-0101", 6)])
        self.assertEqual(self.inv.obtener_repuesto("REP-0101").stock, 40)

    def test_venta_descuenta_stock_y_emite_factura(self):
        cotizacion = self.ventas.crear_cotizacion(
            "CLI-001", "VEN-002", [("REP-0101", 6)]
        )
        comprobante = self.ventas.convertir_en_comprobante(cotizacion.codigo)
        self.assertTrue(comprobante.codigo.startswith("FAC"))
        self.assertEqual(self.inv.obtener_repuesto("REP-0101").stock, 34)
        self.assertEqual(cotizacion.estado, "FACTURADA")

    def test_persona_natural_recibe_boleta(self):
        cotizacion = self.ventas.crear_cotizacion(
            "CLI-004", "VEN-002", [("REP-0101", 2)]
        )
        comprobante = self.ventas.convertir_en_comprobante(cotizacion.codigo)
        self.assertTrue(comprobante.codigo.startswith("BOL"))

    def test_cotizaciones_por_vencer(self):
        hoy = date.today()
        self.ventas.crear_cotizacion("CLI-001", "VEN-002", [("REP-0101", 1)],
                                     hoy - timedelta(days=12))
        self.ventas.crear_cotizacion("CLI-004", "VEN-002", [("REP-0101", 1)], hoy)
        por_vencer = self.ventas.cotizaciones_por_vencer(dias=5)
        self.assertEqual(len(por_vencer), 1)

    def test_reporte_de_utilidad(self):
        hoy = date.today()
        self.ventas.venta_directa("CLI-001", "VEN-002",
                                  [("REP-0101", 6), ("REP-0310", 2)], hoy)
        resumen = self.reportes.resumen_periodo(hoy.year, hoy.month)
        self.assertEqual(resumen["ventas_netas"], 940.50)
        self.assertEqual(resumen["costo_ventas"], 680.00)
        self.assertEqual(resumen["utilidad_bruta"], 260.50)

    def test_comisiones(self):
        hoy = date.today()
        self.ventas.venta_directa("CLI-001", "VEN-002",
                                  [("REP-0101", 6), ("REP-0310", 2)], hoy)
        fila = self.reportes.comisiones(hoy.year, hoy.month)[0]
        self.assertEqual(fila["codigo"], "VEN-002")
        self.assertEqual(fila["comision"], round(940.50 * 0.02, 2))

    def test_historial_filtra_por_vendedor(self):
        self.ventas.crear_cotizacion("CLI-001", "VEN-002", [("REP-0101", 1)])
        self.assertEqual(len(self.ventas.historial(vendedor="VEN-002")), 1)
        self.assertEqual(len(self.ventas.historial(vendedor="VEN-001")), 0)


class TestPersistencia(unittest.TestCase):
    def test_guardar_y_cargar(self):
        import os
        import tempfile

        from src.persistencia import almacenamiento
        from src.persistencia.datos_demo import cargar_demo

        inv = Inventario()
        ventas = GestorVentas(inv)
        cargar_demo(inv, ventas)
        ruta = os.path.join(tempfile.mkdtemp(), "datos.json")
        almacenamiento.guardar(inv, ventas, ruta)

        inv2 = Inventario()
        ventas2 = GestorVentas(inv2)
        almacenamiento.cargar(inv2, ventas2, ruta)
        self.assertEqual(inv2.total_repuestos(), inv.total_repuestos())
        self.assertEqual(len(ventas2.cotizaciones), len(ventas.cotizaciones))
        self.assertEqual(inv2.valorizacion_total(), inv.valorizacion_total())


if __name__ == "__main__":
    unittest.main()
