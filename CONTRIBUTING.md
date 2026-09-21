# Cómo trabajamos en el repositorio

## Reglas básicas
1. Cada integrante trabaja con **su propia cuenta** y hace **sus propios commits**.
2. Antes de empezar a trabajar: `git pull`. Después de terminar: `git add .`, `git commit -m "..."`, `git push`.
3. Un commit = un cambio pequeño y claro. No subir archivos temporales.
4. Nadie sube el trabajo de otro con su cuenta: el historial debe mostrar el aporte real de cada uno.

## Formato de los mensajes de commit
`tipo(area): descripción corta`

Tipos: `docs` (informe), `diag` (diagramas), `feat` (nueva funcionalidad), `fix` (corrección), `test` (pruebas), `refactor`.

Ejemplos por rol:
- `docs(problema): agrega descripcion del problema y generalidades de la empresa`
- `docs(as-is): agrega el proceso actual y su diagrama`
- `docs(alternativas): agrega comparacion de alternativas y proceso TO-BE`
- `docs(historias): agrega historias de usuario priorizadas`
- `docs(pantallas): agrega diseño de pantallas del menu y ventas`
- `feat(producto): agrega clase Producto y ProductoPerecible`
- `test(venta): agrega pruebas del calculo de IGV y descuento`

## Ramas (opcional, recomendado)
- `main`: versión estable.
- Una rama por integrante o tarea: `git checkout -b feature/nombre-tarea`. Se une a `main` con Pull Request revisado por otro integrante.
