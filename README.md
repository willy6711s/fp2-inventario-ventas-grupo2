# Sistema de Control de Inventario y Cotizaciones de Repuestos

**Caso: Ferreyros S.A. — Grupo 2**
Fundamentos de Programación 2 (1FIS0275) · Ciclo 2026-02 · UPC
Docente: Juan Carlos Fernández Sánchez

Prototipo por consola, escrito en Python con programación orientada a objetos, que
apoya el proceso de **cotización y venta de repuestos**: catálogo de repuestos y kits,
clientes y proveedores, cotizaciones con descuento e IGV, conversión a factura o
boleta, control de stock con alertas y reportes de utilidad, valorización y comisiones.

## Cómo ejecutarlo

Requiere **Python 3.9 o superior**. No usa librerías externas.

```bash
git clone <url-del-repositorio>
cd fp2-inventario-ventas-grupo2

python main.py            # inicia con datos de ejemplo
python main.py --vacio    # inicia sin datos
```

## Cómo correr las pruebas

```bash
python -m unittest discover -s tests -t . -v
```

Son 55 pruebas unitarias sobre los métodos de negocio: cálculo de subtotal,
descuento, IGV y total; control de stock; vigencia de cotizaciones; emisión del
comprobante correcto; comisiones y utilidad; y el manejo de excepciones.

## Estructura del proyecto

```
fp2-inventario-ventas-grupo2/
├── main.py                     # punto de entrada (menú principal)
├── src/
│   ├── config.py               # reglas de negocio (IGV, descuento, comisión, validez)
│   ├── excepciones.py          # excepciones propias del sistema
│   ├── modelos/                # clases del dominio
│   │   ├── persona.py          # Persona -> Cliente, Vendedor
│   │   ├── proveedor.py        # Proveedor
│   │   ├── repuesto.py         # Repuesto -> RepuestoIndividual, KitRepuestos
│   │   ├── documento.py        # Documento -> Cotizacion, Comprobante -> Factura, Boleta
│   │   └── movimiento.py       # MovimientoStock
│   ├── servicios/
│   │   ├── inventario.py       # catálogo, stock, alertas, valorización
│   │   ├── ventas.py           # clientes, cotizaciones, ventas, historial
│   │   └── reportes.py         # utilidad, margen, comisiones, ranking
│   ├── persistencia/
│   │   ├── almacenamiento.py   # guardar y cargar en JSON
│   │   └── datos_demo.py       # datos de ejemplo del informe
│   ├── utils/validaciones.py   # validaciones de RUC, DNI, códigos y números
│   └── ui/                     # menús y formato de consola
├── tests/                      # pruebas unitarias (unittest)
├── docs/                       # diagrama de clases e historias de usuario
└── datos/                      # archivos JSON generados por el sistema
```

## Reglas de negocio (`src/config.py`)

| Regla | Valor |
|---|---|
| IGV | 18 % |
| Descuento por volumen | 5 % cuando el subtotal supera S/ 900 |
| Comisión del vendedor | 2 % sobre ventas netas del periodo |
| Validez de la cotización | 15 días |
| Descuento de kit | 10 % sobre la suma de sus componentes |
| Moneda | Soles (S/) |

Todo está centralizado en `config.py`: cambiar la tasa de impuesto o el descuento no
obliga a tocar el resto del código (factores globales del ABET Student Outcome 2).

## Conceptos de POO aplicados

| Concepto | Dónde se ve |
|---|---|
| **Clases y objetos** | `Repuesto`, `Proveedor`, `Cliente`, `Vendedor`, `Cotizacion`, `LineaDetalle`, `MovimientoStock`, `Inventario` |
| **Herencia** | `Repuesto -> RepuestoIndividual, KitRepuestos` · `Documento -> Cotizacion, Comprobante -> Factura, Boleta` · `Persona -> Cliente, Vendedor` |
| **Polimorfismo** | `precio_unitario()` (el kit suma sus componentes con descuento) y `serie`, `titulo`, `pie()` (cada documento se emite distinto) |
| **Encapsulamiento** | Los diccionarios de `Inventario` y `GestorVentas` son privados; se accede por métodos que validan |
| **Composición** | `Cotizacion` contiene varias `LineaDetalle`; `KitRepuestos` agrupa repuestos |
| **Abstracción** | `Repuesto`, `Persona` y `Documento` son clases abstractas (`ABC`) |
| **Excepciones** | `StockInsuficienteError`, `DatoInvalidoError`, `CotizacionVencidaError`, `EntidadNoEncontradaError`, `EntidadDuplicadaError`, `OperacionNoPermitidaError` |

## Historias de usuario cubiertas

Las 16 historias del informe están implementadas: catálogo (HU01–HU03), proveedores
(HU04), clientes (HU05), cotización y cálculo (HU06–HU07), facturación (HU08),
movimientos de stock (HU09), alertas (HU10), seguimiento de cotizaciones (HU11),
comisiones (HU12), valorización (HU13), utilidad (HU14), historial (HU15) y
persistencia en archivo (HU16). El detalle está en `docs/historias_usuario.md`.

## Equipo — Grupo 2

| Integrante | Código | Responsabilidad principal |
|---|---|---|
| Anthony Jeremy Astohuayhua Valle | U20261E777 | Empresa, problema y coordinación del informe |
| Junior Antonio Chavez Correa | U202619576 | Proceso AS-IS y diagrama de clases |
| Max Francisco Ponce Huaman | U202526210 | Alternativas, TO-BE y diagrama de clases |
| Ariana Stefany Rojas Solis | U20261A212 | Historias de usuario, cronograma y pruebas |
| Willy Leonardo Siccha Delgado | U202614280 | Diseño de pantallas, evidencias e informe final |
