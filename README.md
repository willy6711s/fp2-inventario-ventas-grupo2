# Sistema de Control de Inventario y Ventas – Ferretería Constructor Norte S.A.C.

Trabajo Final del curso **1FIS0275 – Fundamentos de Programación 2** (UPC, Ingeniería de Sistemas).
Docente: Juan Carlos Fernández Sánchez · **Grupo 2**

## Descripción
Programa orientado a objetos en **Python** que controla el inventario y las ventas de una ferretería:
registro, búsqueda y listado de productos, proveedores y clientes; ventas con cálculo de descuento e IGV (18 %),
emisión de boleta o factura, alertas de stock mínimo y vencimientos, comisiones de vendedores,
valorización del inventario y utilidad.

## Integrantes y roles
| Integrante | Aporte al proyecto | Usuario de GitHub |
|---|---|---|
| Anthony Jeremy Astohuayhua Valle | Definió la empresa y el problema, generalidades (misión, visión, organigrama), coordinación del informe final | @usuario1 |
| Junior Antonio Chavez Correa | Proceso actual (AS-IS) y diagrama de clases | @usuario2 |
| Max Francisco Ponce Huaman | Alternativas de solución, proceso mejorado (TO-BE) y diagrama de clases | @usuario3 |
| Ariana Stefany Rojas Solis | Historias de usuario, cronograma en Trello, bibliografía y pruebas | @usuario4 |
| Willy Leonardo Siccha Delgado | Diseño de pantallas, evidencias y anexos, informe final | @willy6711s |

## Informe
- Hito 1 (Trabajo Parcial TB1): [`docs/Informe_Hito1_Grupo2.docx`](docs/Informe_Hito1_Grupo2.docx) · [PDF](docs/Informe_Hito1_Grupo2.pdf)

## Funcionalidades (historias de usuario del informe)
| ID | Funcionalidad | Tipo | Prioridad |
|---|---|---|---|
| HU01 | Registrar productos (perecibles y no perecibles) | Control | Alta |
| HU02 | Buscar productos por código o nombre | Control | Alta |
| HU03 | Listar, modificar y dar de baja productos | Control | Alta |
| HU04 | Registrar proveedores | Control | Media |
| HU05 | Registrar y buscar clientes (DNI o RUC) | Control | Alta |
| HU06 | Registrar una venta con varios productos y validar stock | Control | Alta |
| HU07 | Calcular subtotal, descuento por volumen, IGV (18 %) y total | Cálculo | Alta |
| HU08 | Emitir boleta o factura según el tipo de cliente | Control | Alta |
| HU09 | Registrar ingresos de mercadería y ajustes de stock | Control | Alta |
| HU10 | Alertas de productos con stock igual o menor al mínimo | Control | Alta |
| HU11 | Ver productos próximos a vencer | Control | Media |
| HU12 | Calcular la comisión de cada vendedor | Cálculo | Media |
| HU13 | Valorización del inventario (stock × costo) | Cálculo | Media |
| HU14 | Utilidad bruta y margen por periodo | Cálculo | Media |
| HU15 | Historial de ventas por fecha, cliente o vendedor | Control | Media |
| HU16 | Guardar y cargar la información en archivo | Control | Baja |

**Reglas de negocio:** IGV 18 %; descuento por volumen del 5 % cuando el subtotal supera S/ 400; comisión del vendedor del 2 % sobre ventas netas del mes; stock mínimo definido por producto; alerta de vencimiento a 30 días.

## Estructura del repositorio
```
docs/    Informe del proyecto (Word y PDF)
src/     Código fuente en Python (Hito 2)
tests/   Pruebas de los métodos de negocio con unittest (Hito 2)
```

## Cómo ejecutar (se completará en el Hito 2)
```bash
python src/main.py
```

## Cómo ejecutar las pruebas (Hito 2)
```bash
python -m unittest discover -s tests
```

## Hitos
- **Hito 1 (Semana 4):** informe parcial – análisis del problema, solución, historias de usuario, cronograma y diseño de pantallas.
- **Hito 2 (Semana 7):** diagrama de clases, programa en Python, pruebas, informe final y video.

## Gestión del proyecto
Tablero de Trello: https://trello.com/b/VVIiCeWP/fp2-grupo-2
