"""Pruebas de la jerarquía de repuestos (herencia, polimorfismo y stock)."""

import unittest

from src.excepciones import DatoInvalidoError, StockInsuficienteError
from src.modelos.repuesto import KitRepuestos, RepuestoIndividual


class TestRepuestoIndividual(unittest.TestCase):
    def setUp(self):
        self.filtro = RepuestoIndividual(
            "REP-0101", "Filtro de aceite de motor", "Caterpillar", "Filtros",
            60.00, 85.00, 40, 10, "PRV-001"
        )

    def test_precio_unitario_es_precio_venta(self):
        self.assertEqual(self.filtro.precio_unitario(), 85.00)

    def test_tipo_y_detalle(self):
        self.assertEqual(self.filtro.tipo, "Individual")
        self.assertIn("REP-0101", self.filtro.detalle())

    def test_descontar_stock(self):
        self.filtro.descontar_stock(6)
        self.assertEqual(self.filtro.stock, 34)

    def test_descontar_mas_de_lo_disponible(self):
        with self.assertRaises(StockInsuficienteError):
            self.filtro.descontar_stock(50)

    def test_aumentar_y_ajustar_stock(self):
        self.filtro.aumentar_stock(10)
        self.assertEqual(self.filtro.stock, 50)
        self.filtro.ajustar_stock(45)
        self.assertEqual(self.filtro.stock, 45)

    def test_alerta_de_stock_minimo(self):
        self.assertFalse(self.filtro.necesita_reposicion())
        self.filtro.ajustar_stock(10)
        self.assertTrue(self.filtro.necesita_reposicion())

    def test_valorizacion(self):
        self.assertEqual(self.filtro.valorizacion(), 2400.00)

    def test_precio_venta_menor_al_costo(self):
        with self.assertRaises(DatoInvalidoError):
            RepuestoIndividual("REP-0999", "Pieza", "CAT", "Filtros", 100, 80)

    def test_codigo_invalido(self):
        with self.assertRaises(DatoInvalidoError):
            RepuestoIndividual("XX1", "Pieza", "CAT", "Filtros", 10, 20)

    def test_precio_no_numerico(self):
        with self.assertRaises(DatoInvalidoError):
            RepuestoIndividual("REP-0999", "Pieza", "CAT", "Filtros", "abc", 20)


class TestKitRepuestos(unittest.TestCase):
    def setUp(self):
        self.a = RepuestoIndividual("REP-0101", "Filtro de aceite", "CAT", "Filtros",
                                    60, 85, 40, 10)
        self.b = RepuestoIndividual("REP-0102", "Filtro de combustible", "CAT",
                                    "Filtros", 48, 70, 20, 10)
        self.kit = KitRepuestos("REP-0250", "Kit de filtros (500 h)", "CAT",
                                "Kits", 180, 270, 5, 3, horas_servicio=500,
                                descuento_kit=0.10)

    def test_precio_sin_componentes_usa_precio_base(self):
        self.assertEqual(self.kit.precio_unitario(), 270.00)

    def test_precio_polimorfico_con_componentes(self):
        self.kit.agregar_componente(self.a, 1)
        self.kit.agregar_componente(self.b, 1)
        # (85 + 70) * 0.90 = 139.50
        self.assertEqual(self.kit.precio_unitario(), 139.50)

    def test_kit_no_se_contiene_a_si_mismo(self):
        with self.assertRaises(DatoInvalidoError):
            self.kit.agregar_componente(self.kit, 1)

    def test_tipo_del_kit(self):
        self.assertEqual(self.kit.tipo, "Kit")

    def test_polimorfismo_en_lista_mixta(self):
        articulos = [self.a, self.kit]
        tipos = [articulo.tipo for articulo in articulos]
        self.assertEqual(tipos, ["Individual", "Kit"])


if __name__ == "__main__":
    unittest.main()
