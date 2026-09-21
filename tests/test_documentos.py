"""Pruebas de cálculos de cotización, factura y boleta (HU06, HU07, HU08)."""

import unittest
from datetime import date, timedelta

from src.excepciones import (
    CotizacionVencidaError,
    OperacionNoPermitidaError,
    StockInsuficienteError,
)
from src.modelos.documento import Boleta, Cotizacion, Factura
from src.modelos.persona import Cliente, Vendedor
from src.modelos.repuesto import RepuestoIndividual


class TestCalculosCotizacion(unittest.TestCase):
    def setUp(self):
        self.empresa = Cliente("CLI-001", "Minera Ejemplo S.A.C.", "20512345678")
        self.persona = Cliente("CLI-004", "Carlos Mendoza", "45123789")
        self.vendedor = Vendedor("VEN-002", "Diego Salas", "45667788")
        self.filtro = RepuestoIndividual("REP-0101", "Filtro de aceite", "CAT",
                                         "Filtros", 60, 85, 40, 10)
        self.sello = RepuestoIndividual("REP-0310", "Kit de sellos", "CAT",
                                        "Sellos", 160, 240, 10, 5)

    def _cotizacion_del_informe(self):
        cotizacion = Cotizacion(45, self.empresa, self.vendedor, date(2026, 9, 20))
        cotizacion.agregar_linea(self.filtro, 6)
        cotizacion.agregar_linea(self.sello, 2)
        return cotizacion

    def test_subtotal(self):
        self.assertEqual(self._cotizacion_del_informe().subtotal, 990.00)

    def test_descuento_por_volumen(self):
        self.assertEqual(self._cotizacion_del_informe().descuento, 49.50)

    def test_base_imponible(self):
        self.assertEqual(self._cotizacion_del_informe().base_imponible, 940.50)

    def test_igv(self):
        self.assertEqual(self._cotizacion_del_informe().igv, 169.29)

    def test_total(self):
        self.assertEqual(self._cotizacion_del_informe().total, 1109.79)

    def test_sin_descuento_bajo_el_umbral(self):
        cotizacion = Cotizacion(1, self.empresa, self.vendedor)
        cotizacion.agregar_linea(self.filtro, 2)  # 170.00
        self.assertEqual(cotizacion.descuento, 0.00)
        self.assertEqual(cotizacion.total, 200.60)

    def test_codigo_correlativo(self):
        self.assertEqual(self._cotizacion_del_informe().codigo, "COT-000045")

    def test_no_permite_cantidad_mayor_al_stock(self):
        cotizacion = Cotizacion(2, self.empresa, self.vendedor)
        with self.assertRaises(StockInsuficienteError):
            cotizacion.agregar_linea(self.filtro, 50)

    def test_no_emite_documento_vacio(self):
        cotizacion = Cotizacion(3, self.empresa, self.vendedor)
        with self.assertRaises(OperacionNoPermitidaError):
            cotizacion.emitir()

    def test_vigencia(self):
        cotizacion = Cotizacion(4, self.empresa, self.vendedor, date(2026, 9, 20))
        self.assertEqual(cotizacion.fecha_vencimiento, date(2026, 10, 5))
        self.assertEqual(cotizacion.dias_para_vencer(date(2026, 9, 30)), 5)

    def test_cotizacion_vencida_no_se_aprueba(self):
        antigua = date.today() - timedelta(days=30)
        cotizacion = Cotizacion(5, self.empresa, self.vendedor, antigua)
        cotizacion.agregar_linea(self.filtro, 1)
        with self.assertRaises(CotizacionVencidaError):
            cotizacion.aprobar()

    def test_utilidad_del_documento(self):
        cotizacion = self._cotizacion_del_informe()
        # base 940.50 - costo (6*60 + 2*160) = 940.50 - 680 = 260.50
        self.assertEqual(cotizacion.utilidad, 260.50)


class TestComprobantes(unittest.TestCase):
    def setUp(self):
        self.empresa = Cliente("CLI-001", "Minera Ejemplo S.A.C.", "20512345678")
        self.persona = Cliente("CLI-004", "Carlos Mendoza", "45123789")
        self.vendedor = Vendedor("VEN-001", "Rosa Quispe", "44556677")
        self.filtro = RepuestoIndividual("REP-0101", "Filtro de aceite", "CAT",
                                         "Filtros", 60, 85, 40, 10)

    def test_factura_solo_para_empresas(self):
        with self.assertRaises(OperacionNoPermitidaError):
            Factura(1, self.persona, self.vendedor)

    def test_series_polimorficas(self):
        factura = Factura(1, self.empresa, self.vendedor)
        boleta = Boleta(1, self.persona, self.vendedor)
        self.assertEqual(factura.codigo, "FAC-000001")
        self.assertEqual(boleta.codigo, "BOL-000001")
        self.assertNotEqual(factura.titulo, boleta.titulo)

    def test_descuento_de_stock_una_sola_vez(self):
        factura = Factura(2, self.empresa, self.vendedor)
        factura.agregar_linea(self.filtro, 5)
        factura.descontar_stock()
        self.assertEqual(self.filtro.stock, 35)
        with self.assertRaises(OperacionNoPermitidaError):
            factura.descontar_stock()

    def test_cliente_define_el_documento(self):
        self.assertEqual(self.empresa.documento_que_corresponde(), "FACTURA")
        self.assertEqual(self.persona.documento_que_corresponde(), "BOLETA")


if __name__ == "__main__":
    unittest.main()
