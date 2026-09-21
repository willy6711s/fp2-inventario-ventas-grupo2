"""Carga de datos de ejemplo para poder probar el sistema de inmediato.

Los códigos y montos coinciden con las pantallas del informe (Cap. 2).
"""

from datetime import date, timedelta

from src.modelos.persona import Cliente, Vendedor
from src.modelos.proveedor import Proveedor
from src.modelos.repuesto import KitRepuestos, RepuestoIndividual


def cargar_demo(inventario, ventas):
    # Proveedores
    inventario.registrar_proveedor(
        Proveedor("PRV-001", "Caterpillar Perú S.A.", "20100055555",
                  "01-4567890", "ventas@catperu.com", "Área de repuestos")
    )
    inventario.registrar_proveedor(
        Proveedor("PRV-002", "Sellos y Filtros Andinos S.A.C.", "20512223334",
                  "01-7778899", "contacto@sfandinos.pe", "Luis Ramos")
    )

    # Repuestos individuales
    datos_repuestos = [
        ("REP-0101", "Filtro de aceite de motor", "Caterpillar", "Filtros", 60.00, 85.00, 40, 10, "PRV-001"),
        ("REP-0102", "Filtro de combustible", "Caterpillar", "Filtros", 48.00, 70.00, 8, 10, "PRV-001"),
        ("REP-0103", "Filtro de aire primario", "Caterpillar", "Filtros", 90.00, 135.00, 25, 8, "PRV-001"),
        ("REP-0201", "Sello hidráulico 45 mm", "Caterpillar", "Sellos", 35.00, 55.00, 60, 15, "PRV-002"),
        ("REP-0202", "Manguera hidráulica 3/4", "Metso", "Hidráulica", 110.00, 165.00, 18, 6, "PRV-002"),
        ("REP-0203", "Zapata de oruga", "Caterpillar", "Tren de rodamiento", 480.00, 720.00, 12, 4, "PRV-001"),
        ("REP-0204", "Perno de zapata", "Caterpillar", "Tren de rodamiento", 12.00, 20.00, 200, 50, "PRV-001"),
        ("REP-0205", "Bomba de agua", "Massey Ferguson", "Motor", 620.00, 930.00, 5, 3, "PRV-001"),
    ]
    for datos in datos_repuestos:
        inventario.registrar_repuesto(RepuestoIndividual(*datos))

    # Kits
    kit_filtros = KitRepuestos("REP-0250", "Kit de filtros (500 h)", "Caterpillar",
                               "Kits de mantenimiento", 180.00, 270.00, 5, 3,
                               "PRV-001", horas_servicio=500)
    inventario.registrar_repuesto(kit_filtros)
    inventario.armar_kit("REP-0250", [("REP-0101", 1), ("REP-0102", 1), ("REP-0103", 1)])

    kit_sellos = KitRepuestos("REP-0310", "Kit de sellos hidráulicos", "Caterpillar",
                              "Kits de mantenimiento", 160.00, 240.00, 3, 5,
                              "PRV-002", horas_servicio=1000)
    # Este kit se deja con precio de lista (sin componentes) para que los montos
    # coincidan con la pantalla 4 del informe: S/ 240.00 por unidad.
    inventario.registrar_repuesto(kit_sellos)

    # Vendedores
    ventas.registrar_vendedor(
        Vendedor("VEN-001", "Vendedor A - Rosa Quispe", "44556677",
                 "987654321", "rquispe@ferreyros.com.pe", 0.02, 9000.00)
    )
    ventas.registrar_vendedor(
        Vendedor("VEN-002", "Vendedor B - Diego Salas", "45667788",
                 "987123456", "dsalas@ferreyros.com.pe", 0.02, 9000.00)
    )

    # Clientes
    ventas.registrar_cliente(
        Cliente("CLI-001", "Minera Ejemplo S.A.C.", "20512345678",
                "01-3334455", "compras@mineraejemplo.pe", "Minería")
    )
    ventas.registrar_cliente(
        Cliente("CLI-002", "Constructora Ejemplo S.A.", "20487654321",
                "01-2223344", "logistica@constructora.pe", "Construcción")
    )
    ventas.registrar_cliente(
        Cliente("CLI-003", "Agrícola del Norte E.I.R.L.", "20999888777",
                "074-556677", "compras@agricolanorte.pe", "Agricultura")
    )
    ventas.registrar_cliente(
        Cliente("CLI-004", "Carlos Mendoza Ríos", "45123789",
                "999888777", "cmendoza@correo.com", "Independiente")
    )

    hoy = date.today()

    # Cotización de la pantalla 4 del informe (6 filtros + 2 kits de sellos)
    cotizacion = ventas.crear_cotizacion(
        "CLI-001", "VEN-002", [("REP-0101", 6), ("REP-0310", 2)], hoy
    )

    # Cotizaciones pendientes con distintos vencimientos (pantalla 5)
    ventas.crear_cotizacion(
        "CLI-002", "VEN-001", [("REP-0203", 4), ("REP-0204", 20)],
        hoy - timedelta(days=10)
    )
    ventas.crear_cotizacion(
        "CLI-003", "VEN-001", [("REP-0103", 3)], hoy - timedelta(days=5)
    )

    # Ventas ya concretadas para alimentar el reporte de utilidad y comisiones
    ventas.venta_directa("CLI-002", "VEN-001",
                         [("REP-0205", 2), ("REP-0202", 4)], hoy)
    ventas.venta_directa("CLI-004", "VEN-002",
                         [("REP-0201", 6), ("REP-0204", 10)], hoy)

    return cotizacion
