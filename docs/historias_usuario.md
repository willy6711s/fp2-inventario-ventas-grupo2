# Historias de usuario y su implementación

Tipo: C = control, K = cálculo. Las 16 historias del informe están cubiertas.

| ID | Historia de usuario | Tipo | Prior. | Dónde está implementada | Prueba |
|----|---------------------|------|--------|-------------------------|--------|
| HU01 | Registrar repuestos individuales y kits | C | Alta | `Inventario.registrar_repuesto()`, `KitRepuestos` | `test_inventario.py` |
| HU02 | Buscar repuestos por número de parte o nombre | C | Alta | `Inventario.buscar()` | `test_busqueda_por_nombre`, `test_busqueda_por_codigo` |
| HU03 | Listar, modificar y dar de baja repuestos | C | Alta | `listar_repuestos()`, `modificar_repuesto()`, `dar_de_baja()` | `test_baja_saca_del_listado` |
| HU04 | Registrar proveedores | C | Media | `Inventario.registrar_proveedor()` | `test_proveedor_inexistente_al_registrar` |
| HU05 | Registrar y buscar clientes (RUC o DNI) | C | Alta | `GestorVentas.registrar_cliente()`, `obtener_cliente()` | `test_busqueda_de_cliente_por_ruc` |
| HU06 | Cotización con varios repuestos y validación de stock | C | Alta | `GestorVentas.crear_cotizacion()`, `Documento.agregar_linea()` | `test_cotizacion_con_totales_del_informe` |
| HU07 | Calcular subtotal, descuento, IGV y total | K | Alta | Propiedades de `Documento` | `test_documentos.py` (subtotal, descuento, IGV, total) |
| HU08 | Convertir cotización en factura o boleta | C | Alta | `convertir_en_comprobante()`, `Factura`, `Boleta` | `test_persona_natural_recibe_boleta` |
| HU09 | Registrar ingresos y ajustes de stock | C | Alta | `registrar_ingreso()`, `registrar_ajuste()` | `test_ingreso_actualiza_stock_y_movimiento` |
| HU10 | Alertas de stock igual o menor al mínimo | C | Alta | `Inventario.alertas_stock()` | `test_alertas_de_stock` |
| HU11 | Ver cotizaciones pendientes y por vencer | C | Media | `cotizaciones_pendientes()`, `cotizaciones_por_vencer()` | `test_cotizaciones_por_vencer` |
| HU12 | Calcular comisión por vendedor | K | Media | `GeneradorReportes.comisiones()`, `Vendedor.calcular_comision()` | `test_comisiones` |
| HU13 | Valorización del inventario (stock × costo) | K | Media | `Repuesto.valorizacion()`, `Inventario.valorizacion_total()` | `test_valorizacion_total` |
| HU14 | Utilidad bruta y margen por periodo | K | Media | `GeneradorReportes.resumen_periodo()` | `test_reporte_de_utilidad` |
| HU15 | Historial de cotizaciones y ventas | C | Media | `GestorVentas.historial()` | `test_historial_filtra_por_vendedor` |
| HU16 | Guardar y cargar la información en archivo | C | Baja | `src/persistencia/almacenamiento.py` | `test_guardar_y_cargar` |

## Manejo de errores (pantalla 7 del informe)

| Situación | Excepción | Mensaje al usuario |
|---|---|---|
| Se cotiza más de lo disponible | `StockInsuficienteError` | Stock insuficiente para REP-0102. Disponible: 8. |
| RUC con menos de 11 dígitos | `DatoInvalidoError` | El RUC debe tener 11 dígitos. |
| Precio no numérico | `DatoInvalidoError` | Ingrese un valor numérico válido en 'precio de venta'. |
| Repuesto que no existe | `EntidadNoEncontradaError` | No existe el repuesto REP-9999. |
| Código repetido | `EntidadDuplicadaError` | Ya existe un repuesto con el código REP-0101. |
| Cotización fuera de plazo | `CotizacionVencidaError` | La cotización COT-000005 venció el 06/09/2026. |
| Factura a persona natural | `OperacionNoPermitidaError` | Solo se emite factura a clientes con RUC. Use una boleta. |
