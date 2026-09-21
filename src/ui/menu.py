"""Menús por consola del sistema (pantallas 1 a 7 del informe)."""

from datetime import date

from src.config import ARCHIVO_DATOS, MONEDA
from src.excepciones import ErrorSistema
from src.modelos.persona import Cliente, Vendedor
from src.modelos.proveedor import Proveedor
from src.modelos.repuesto import KitRepuestos, RepuestoIndividual
from src.persistencia import almacenamiento
from src.servicios.inventario import Inventario
from src.servicios.reportes import GeneradorReportes
from src.servicios.ventas import GestorVentas
from src.ui import formato as f


class Aplicacion:
    def __init__(self, inventario=None, ventas=None):
        self.inventario = inventario or Inventario()
        self.ventas = ventas or GestorVentas(self.inventario)
        self.reportes = GeneradorReportes(self.inventario, self.ventas)

    # ---------------- utilidades de entrada ----------------
    @staticmethod
    def _pedir(mensaje):
        return input(mensaje).strip()

    def _pedir_opcion(self, mensaje, opciones):
        while True:
            valor = self._pedir(mensaje)
            if valor in opciones:
                return valor
            print(f.error(f"Opción inválida. Use: {', '.join(opciones)}."))

    def _continuar(self):
        input("\n Presione ENTER para continuar...")

    # ---------------- menú principal (pantalla 1) ----------------
    def menu_principal(self):
        opciones = {
            "1": ("Gestión de repuestos y kits", self.menu_repuestos),
            "2": ("Gestión de proveedores", self.menu_proveedores),
            "3": ("Gestión de clientes y vendedores", self.menu_clientes),
            "4": ("Registrar cotización / venta", self.menu_cotizaciones),
            "5": ("Movimientos de stock (ingresos / ajustes)", self.menu_movimientos),
            "6": ("Reportes (stock bajo, pendientes, utilidad)", self.menu_reportes),
            "7": ("Comisiones de vendedores", self.reporte_comisiones),
            "8": ("Guardar / cargar datos", self.menu_datos),
        }
        while True:
            print()
            print(f.titulo("Sistema de inventario y cotizaciones - Ferreyros"))
            for clave, (etiqueta, _) in opciones.items():
                print(f"   [{clave}] {etiqueta}")
            print("   [0] Salir")
            print(f.separador())
            eleccion = self._pedir("   Seleccione una opción: ")
            if eleccion == "0":
                print(f.exito("Gracias por usar el sistema. ¡Hasta pronto!"))
                break
            if eleccion in opciones:
                try:
                    opciones[eleccion][1]()
                except ErrorSistema as error:
                    print(f.error(str(error)))
                    self._continuar()
                except KeyboardInterrupt:
                    print("\n" + f.aviso("Operación cancelada."))
            else:
                print(f.error("Opción no válida. Intente nuevamente."))

    # ---------------- repuestos ----------------
    def menu_repuestos(self):
        while True:
            print()
            print(f.subtitulo("Repuestos y kits"))
            print("   [1] Registrar repuesto individual")
            print("   [2] Registrar kit de repuestos")
            print("   [3] Buscar repuesto (HU02)")
            print("   [4] Listar catálogo")
            print("   [5] Modificar repuesto")
            print("   [6] Dar de baja repuesto")
            print("   [0] Volver")
            eleccion = self._pedir("   Opción: ")
            try:
                if eleccion == "1":
                    self.registrar_repuesto(kit=False)
                elif eleccion == "2":
                    self.registrar_repuesto(kit=True)
                elif eleccion == "3":
                    self.buscar_repuesto()
                elif eleccion == "4":
                    print(f.tabla_repuestos(self.inventario.listar_repuestos()))
                    self._continuar()
                elif eleccion == "5":
                    self.modificar_repuesto()
                elif eleccion == "6":
                    codigo = self._pedir("   Código a dar de baja: ")
                    repuesto = self.inventario.dar_de_baja(codigo)
                    print(f.exito(f"{repuesto.codigo} dado de baja."))
                    self._continuar()
                elif eleccion == "0":
                    return
                else:
                    print(f.error("Opción no válida."))
            except ErrorSistema as error:
                print(f.error(str(error)))
                self._continuar()

    def registrar_repuesto(self, kit=False):
        print()
        print(f.subtitulo("Registrar kit" if kit else "Registrar repuesto"))
        codigo = self._pedir("   Código (n.° de parte) ..: ")
        nombre = self._pedir("   Nombre .................: ")
        marca = self._pedir("   Marca ..................: ")
        categoria = self._pedir("   Categoría ..............: ")
        precio_compra = self._pedir("   Precio de compra (S/) ..: ")
        precio_venta = self._pedir("   Precio de venta (S/) ...: ")
        stock = self._pedir("   Stock inicial ..........: ")
        stock_minimo = self._pedir("   Stock mínimo ...........: ")
        proveedor = self._pedir("   Proveedor (código) .....: ") or None
        if kit:
            horas = self._pedir("   Horas de servicio ......: ") or 0
            articulo = KitRepuestos(codigo, nombre, marca, categoria, precio_compra,
                                    precio_venta, stock, stock_minimo, proveedor,
                                    horas_servicio=horas)
        else:
            articulo = RepuestoIndividual(codigo, nombre, marca, categoria,
                                          precio_compra, precio_venta, stock,
                                          stock_minimo, proveedor)
        self.inventario.registrar_repuesto(articulo)
        print(f.exito("Repuesto registrado correctamente."))
        if kit:
            self._armar_componentes(articulo.codigo)
        self._continuar()

    def _armar_componentes(self, codigo_kit):
        componentes = []
        print(f.aviso("Agregue los componentes del kit (ENTER vacío para terminar)."))
        while True:
            codigo = self._pedir("   Código del componente: ")
            if not codigo:
                break
            cantidad = self._pedir("   Cantidad ............: ")
            componentes.append((codigo, cantidad))
        if componentes:
            kit = self.inventario.armar_kit(codigo_kit, componentes)
            print(f.exito(f"Kit armado. Precio calculado: {f.soles(kit.precio_unitario())}"))

    def buscar_repuesto(self):
        print()
        print(f.subtitulo("Buscar repuesto"))
        criterio = self._pedir_opcion(
            "   Buscar por (1=N.° de parte, 2=Nombre): ", ("1", "2")
        )
        texto = self._pedir("   Texto: ")
        por = "codigo" if criterio == "1" else "nombre"
        resultados = self.inventario.buscar(texto, por)
        print()
        print(f.tabla_repuestos(resultados))
        print(f"\n   Resultados: {len(resultados)}")
        for repuesto in resultados:
            if repuesto.necesita_reposicion():
                print(f.aviso(f"{repuesto.codigo} está en stock mínimo ({repuesto.stock})."))
        self._continuar()

    def modificar_repuesto(self):
        codigo = self._pedir("   Código del repuesto: ")
        repuesto = self.inventario.obtener_repuesto(codigo)
        print(f"   {repuesto}")
        campo = self._pedir_opcion(
            "   Campo (1=Precio venta, 2=Stock mínimo, 3=Categoría): ",
            ("1", "2", "3"),
        )
        valor = self._pedir("   Nuevo valor: ")
        mapa = {"1": "precio_venta", "2": "stock_minimo", "3": "categoria"}
        if campo == "1":
            from src.utils.validaciones import validar_decimal
            valor = validar_decimal(valor, "precio de venta", 0.01)
        elif campo == "2":
            from src.utils.validaciones import validar_entero
            valor = validar_entero(valor, "stock mínimo", 0)
        self.inventario.modificar_repuesto(codigo, **{mapa[campo]: valor})
        print(f.exito("Repuesto actualizado."))
        self._continuar()

    # ---------------- proveedores ----------------
    def menu_proveedores(self):
        print()
        print(f.subtitulo("Proveedores"))
        print("   [1] Registrar proveedor")
        print("   [2] Listar proveedores")
        print("   [0] Volver")
        eleccion = self._pedir("   Opción: ")
        if eleccion == "1":
            proveedor = Proveedor(
                self._pedir("   Código (PRV-000) ....: "),
                self._pedir("   Razón social ........: "),
                self._pedir("   RUC .................: "),
                self._pedir("   Teléfono ............: "),
                self._pedir("   Correo ..............: "),
                self._pedir("   Contacto ............: "),
            )
            self.inventario.registrar_proveedor(proveedor)
            print(f.exito("Proveedor registrado."))
            self._continuar()
        elif eleccion == "2":
            for proveedor in self.inventario.listar_proveedores():
                print(f"   {proveedor}")
            self._continuar()

    # ---------------- clientes y vendedores ----------------
    def menu_clientes(self):
        print()
        print(f.subtitulo("Clientes y vendedores"))
        print("   [1] Registrar cliente")
        print("   [2] Buscar cliente")
        print("   [3] Listar clientes")
        print("   [4] Registrar vendedor")
        print("   [5] Listar vendedores")
        print("   [0] Volver")
        eleccion = self._pedir("   Opción: ")
        if eleccion == "1":
            cliente = Cliente(
                self._pedir("   Código (CLI-000) ....: "),
                self._pedir("   Nombre / razón social: "),
                self._pedir("   RUC o DNI ...........: "),
                self._pedir("   Teléfono ............: "),
                self._pedir("   Correo ..............: "),
                self._pedir("   Sector ..............: ") or "General",
            )
            self.ventas.registrar_cliente(cliente)
            print(f.exito(
                f"Cliente registrado. Se le emitirá {cliente.documento_que_corresponde()}."
            ))
            self._continuar()
        elif eleccion == "2":
            texto = self._pedir("   Nombre o documento: ")
            encontrados = self.ventas.buscar_clientes(texto)
            for cliente in encontrados:
                print(f"   {cliente} | {cliente.descripcion()}")
            if not encontrados:
                print(f.aviso("Sin resultados."))
            self._continuar()
        elif eleccion == "3":
            for cliente in self.ventas.listar_clientes():
                print(f"   {cliente}")
            self._continuar()
        elif eleccion == "4":
            vendedor = Vendedor(
                self._pedir("   Código (VEN-000) ....: "),
                self._pedir("   Nombre ..............: "),
                self._pedir("   DNI .................: "),
                self._pedir("   Teléfono ............: "),
                self._pedir("   Correo ..............: "),
                self._pedir("   Tasa de comisión (0.02): ") or 0.02,
                self._pedir("   Meta mensual (S/) ...: ") or 0,
            )
            self.ventas.registrar_vendedor(vendedor)
            print(f.exito("Vendedor registrado."))
            self._continuar()
        elif eleccion == "5":
            for vendedor in self.ventas.listar_vendedores():
                print(f"   {vendedor} | {vendedor.descripcion()}")
            self._continuar()

    # ---------------- cotizaciones y ventas ----------------
    def menu_cotizaciones(self):
        print()
        print(f.subtitulo("Cotizaciones y ventas"))
        print("   [1] Registrar cotización")
        print("   [2] Convertir cotización en factura / boleta")
        print("   [3] Ver una cotización")
        print("   [4] Historial de documentos")
        print("   [0] Volver")
        eleccion = self._pedir("   Opción: ")
        if eleccion == "1":
            self.registrar_cotizacion()
        elif eleccion == "2":
            codigo = self._pedir("   Código de cotización (COT-000001): ")
            comprobante = self.ventas.convertir_en_comprobante(codigo)
            print()
            print(comprobante.emitir())
            self._continuar()
        elif eleccion == "3":
            codigo = self._pedir("   Código de cotización: ")
            print()
            print(self.ventas.obtener_cotizacion(codigo).emitir())
            self._continuar()
        elif eleccion == "4":
            for documento in self.ventas.historial():
                print(f"   {documento}")
            self._continuar()

    def registrar_cotizacion(self):
        print()
        print(f.subtitulo("Registrar cotización"))
        cliente = self._pedir("   Cliente (código o RUC/DNI): ")
        vendedor = self._pedir("   Vendedor (código) ........: ")
        items = []
        print(f.aviso("Agregue repuestos (ENTER vacío en el código para terminar)."))
        while True:
            codigo = self._pedir("   Código del repuesto: ")
            if not codigo:
                break
            cantidad = self._pedir("   Cantidad a cotizar : ")
            try:
                repuesto = self.inventario.obtener_repuesto(codigo)
                from src.utils.validaciones import validar_entero
                cantidad_num = validar_entero(cantidad, "cantidad", 1)
                if not repuesto.hay_disponibilidad(cantidad_num):
                    print(f.error(
                        f"Stock insuficiente para {repuesto.codigo}. "
                        f"Disponible: {repuesto.stock}."
                    ))
                    continue
                items.append((codigo, cantidad_num))
                print(f.exito(
                    f"{repuesto.nombre} x {cantidad_num} = "
                    f"{f.soles(repuesto.precio_unitario() * cantidad_num)}"
                ))
            except ErrorSistema as error:
                print(f.error(str(error)))
        if not items:
            print(f.aviso("No se agregó ningún repuesto; se cancela la cotización."))
            self._continuar()
            return
        cotizacion = self.ventas.crear_cotizacion(cliente, vendedor, items)
        print()
        print(cotizacion.emitir())
        if self._pedir("\n   ¿Convertir ahora en comprobante? (s/n): ").lower() == "s":
            comprobante = self.ventas.convertir_en_comprobante(cotizacion.codigo)
            print()
            print(comprobante.emitir())
        self._continuar()

    # ---------------- movimientos ----------------
    def menu_movimientos(self):
        print()
        print(f.subtitulo("Movimientos de stock"))
        print("   [1] Registrar ingreso de mercadería")
        print("   [2] Ajustar stock por conteo físico")
        print("   [3] Ver historial de movimientos")
        print("   [0] Volver")
        eleccion = self._pedir("   Opción: ")
        if eleccion == "1":
            codigo = self._pedir("   Código del repuesto: ")
            cantidad = self._pedir("   Cantidad ingresada.: ")
            guia = self._pedir("   Guía / documento ..: ")
            movimiento = self.inventario.registrar_ingreso(
                codigo, cantidad, "Ingreso de mercadería", guia
            )
            repuesto = self.inventario.obtener_repuesto(codigo)
            print(f.exito(f"Ingreso registrado. Stock actual: {repuesto.stock}."))
            self._continuar()
        elif eleccion == "2":
            codigo = self._pedir("   Código del repuesto: ")
            stock_real = self._pedir("   Stock contado .....: ")
            self.inventario.registrar_ajuste(codigo, stock_real)
            print(f.exito("Ajuste registrado."))
            self._continuar()
        elif eleccion == "3":
            codigo = self._pedir("   Código (ENTER = todos): ") or None
            for movimiento in self.inventario.historial_movimientos(codigo):
                print(f"   {movimiento}")
            self._continuar()

    # ---------------- reportes ----------------
    def menu_reportes(self):
        print()
        print(f.subtitulo("Reportes"))
        print("   [1] Alertas de stock y cotizaciones por vencer")
        print("   [2] Utilidad y valorización del periodo")
        print("   [3] Repuestos más vendidos")
        print("   [0] Volver")
        eleccion = self._pedir("   Opción: ")
        if eleccion == "1":
            self.reporte_alertas()
        elif eleccion == "2":
            hoy = date.today()
            print()
            print(self.reportes.texto_resumen(hoy.year, hoy.month))
            self._continuar()
        elif eleccion == "3":
            for fila in self.reportes.ranking_repuestos():
                print(
                    f"   {fila['codigo']:<10} {fila['nombre'][:30]:<30} "
                    f"{fila['cantidad']:>5} u. {f.soles(fila['monto']):>15}"
                )
            self._continuar()

    def reporte_alertas(self):
        print()
        print(f.subtitulo("Alertas del inventario"))
        print("   REPUESTOS CON STOCK MÍNIMO")
        print(f"   {'Código':<10} {'Repuesto':<32} {'Stock':>6} {'Mínimo':>7}  Estado")
        alertas = self.inventario.alertas_stock()
        for repuesto in alertas:
            print(
                f"   {repuesto.codigo:<10} {repuesto.nombre[:32]:<32} "
                f"{repuesto.stock:>6} {repuesto.stock_minimo:>7}  REPONER"
            )
        if not alertas:
            print("   (sin alertas de stock)")
        print()
        print("   COTIZACIONES PENDIENTES POR VENCER")
        print(f"   {'N.°':<12} {'Cliente':<32} {'Vence':<12} Días")
        pendientes = self.ventas.cotizaciones_por_vencer(dias=15)
        for cotizacion in pendientes:
            print(
                f"   {cotizacion.codigo:<12} {cotizacion.cliente.nombre[:32]:<32} "
                f"{cotizacion.fecha_vencimiento.strftime('%d/%m/%Y'):<12} "
                f"{cotizacion.dias_para_vencer():>4}"
            )
        if not pendientes:
            print("   (sin cotizaciones por vencer)")
        self._continuar()

    def reporte_comisiones(self):
        hoy = date.today()
        print()
        print(f.subtitulo(f"Comisiones del periodo {hoy.month:02d}/{hoy.year}"))
        print(f"   {'Vendedor':<28} {'Ventas netas':>16} {'Comisión':>14}  Meta")
        for fila in self.reportes.comisiones(hoy.year, hoy.month):
            meta = "-" if fila["cumplio_meta"] is None else (
                "CUMPLIDA" if fila["cumplio_meta"] else "PENDIENTE"
            )
            print(
                f"   {fila['codigo'] + ' ' + fila['nombre'][:20]:<28} "
                f"{f.soles(fila['ventas_netas']):>16} "
                f"{f.soles(fila['comision']):>14}  {meta}"
            )
        self._continuar()

    # ---------------- datos ----------------
    def menu_datos(self):
        print()
        print(f.subtitulo("Guardar y cargar datos"))
        print("   [1] Guardar en archivo")
        print("   [2] Cargar desde archivo")
        print("   [0] Volver")
        eleccion = self._pedir("   Opción: ")
        if eleccion == "1":
            ruta = almacenamiento.guardar(self.inventario, self.ventas)
            print(f.exito(f"Datos guardados en {ruta}."))
            self._continuar()
        elif eleccion == "2":
            self.inventario = Inventario()
            self.ventas = GestorVentas(self.inventario)
            almacenamiento.cargar(self.inventario, self.ventas, ARCHIVO_DATOS)
            self.reportes = GeneradorReportes(self.inventario, self.ventas)
            print(f.exito("Datos cargados correctamente."))
            self._continuar()
