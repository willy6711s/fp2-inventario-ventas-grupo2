"""Pruebas del servicio de inventario (HU01-HU04, HU09, HU10, HU13)."""

import unittest

from src.excepciones import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    StockInsuficienteError,
)
from src.modelos.proveedor import Proveedor
from src.modelos.repuesto import KitRepuestos, RepuestoIndividual
from src.servicios.inventario import Inventario


class TestInventario(unittest.TestCase):
    def setUp(self):
        self.inv = Inventario()
        self.inv.registrar_proveedor(
            Proveedor("PRV-001", "Caterpillar Perú S.A.", "20100055555")
        )
        self.inv.registrar_repuesto(
            RepuestoIndividual("REP-0101", "Filtro de aceite de motor", "CAT",
                               "Filtros", 60, 85, 40, 10, "PRV-001")
        )
        self.inv.registrar_repuesto(
            RepuestoIndividual("REP-0102", "Filtro de combustible", "CAT",
                               "Filtros", 48, 70, 8, 10, "PRV-001")
        )

    def test_no_permite_codigos_duplicados(self):
        with self.assertRaises(EntidadDuplicadaError):
            self.inv.registrar_repuesto(
                RepuestoIndividual("REP-0101", "Otro filtro", "CAT", "Filtros", 10, 20)
            )

    def test_repuesto_inexistente(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.inv.obtener_repuesto("REP-9999")

    def test_proveedor_inexistente_al_registrar(self):
        with self.assertRaises(EntidadNoEncontradaError):
            self.inv.registrar_repuesto(
                RepuestoIndividual("REP-0500", "Pieza", "CAT", "Filtros", 10, 20,
                                   1, 1, "PRV-999")
            )

    def test_busqueda_por_nombre(self):
        resultados = self.inv.buscar("filtro", "nombre")
        self.assertEqual(len(resultados), 2)

    def test_busqueda_por_codigo(self):
        resultados = self.inv.buscar("REP-0102", "codigo")
        self.assertEqual(resultados[0].nombre, "Filtro de combustible")

    def test_alertas_de_stock(self):
        alertas = self.inv.alertas_stock()
        self.assertEqual([r.codigo for r in alertas], ["REP-0102"])

    def test_ingreso_actualiza_stock_y_movimiento(self):
        self.inv.registrar_ingreso("REP-0102", 12, "Compra", "GR-001")
        self.assertEqual(self.inv.obtener_repuesto("REP-0102").stock, 20)
        self.assertEqual(self.inv.historial_movimientos("REP-0102")[-1].tipo, "INGRESO")

    def test_ajuste_por_conteo(self):
        self.inv.registrar_ajuste("REP-0101", 37)
        self.assertEqual(self.inv.obtener_repuesto("REP-0101").stock, 37)

    def test_salida_sin_stock(self):
        with self.assertRaises(StockInsuficienteError):
            self.inv.registrar_salida("REP-0102", 100)

    def test_valorizacion_total(self):
        # 40*60 + 8*48 = 2400 + 384
        self.assertEqual(self.inv.valorizacion_total(), 2784.00)

    def test_baja_saca_del_listado(self):
        self.inv.dar_de_baja("REP-0101")
        codigos = [r.codigo for r in self.inv.listar_repuestos()]
        self.assertNotIn("REP-0101", codigos)

    def test_armar_kit_calcula_precio(self):
        self.inv.registrar_repuesto(
            KitRepuestos("REP-0250", "Kit de filtros (500 h)", "CAT", "Kits",
                         100, 150, 5, 2, "PRV-001", 500, 0.10)
        )
        kit = self.inv.armar_kit("REP-0250", [("REP-0101", 1), ("REP-0102", 1)])
        self.assertEqual(kit.precio_unitario(), 139.50)


if __name__ == "__main__":
    unittest.main()
