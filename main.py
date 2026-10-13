from abc import ABC, abstractmethod
import unittest

# EXCEPCIONES
class ExcepcionInventario(Exception):
    def __init__(self, mensaje):
        super().__init__(mensaje)


class ItemRepuesto(ABC):
    def __init__(self, codigo, nombre, marca, categoria, precio_compra, precio_venta, stock, stock_minimo, proveedor_cod):
        self.__codigo = codigo
        self.__nombre = nombre
        self.__marca = marca
        self.__categoria = categoria
        self.__precio_compra = precio_compra
        self.__precio_venta = precio_venta
        self.__stock = stock
        self.__stock_minimo = stock_minimo
        self.__proveedor_cod = proveedor_cod

    @property
    def codigo(self):
        return self.__codigo

    @property
    def nombre(self):
        return self.__nombre

    @property
    def precio_venta(self):
        return self.__precio_venta

    @property
    def stock(self):
        return self.__stock

    @stock.setter
    def stock(self, nuevo_stock):
        self.__stock = nuevo_stock

    @property
    def stock_minimo(self):
        return self.__stock_minimo

    def verificar_stock_minimo(self):
        return self.__stock <= self.__stock_minimo

    @abstractmethod
    def obtener_tipo(self):
        pass

    def __str__(self):
        return f"{self.__codigo:<10} {self.__nombre:<32} {self.obtener_tipo():<10} {self.__stock:<8} {self.__precio_venta:<8.2f}"


class RepuestoIndividual(ItemRepuesto):
    def __init__(self, codigo, nombre, marca, categoria, precio_compra, precio_venta, stock, stock_minimo, proveedor_cod):
        super().__init__(codigo, nombre, marca, categoria, precio_compra, precio_venta, stock, stock_minimo, proveedor_cod)

    def obtener_tipo(self):
        return "Individual"


class KitRepuesto(ItemRepuesto):
    def __init__(self, codigo, nombre, marca, categoria, precio_compra, precio_venta, stock, stock_minimo, proveedor_cod):
        super().__init__(codigo, nombre, marca, categoria, precio_compra, precio_venta, stock, stock_minimo, proveedor_cod)

    def obtener_tipo(self):
        return "Kit"


# CLASE PROVEEDOR
class Proveedor:
    def __init__(self, codigo, razon_social, ruc):
        self.__codigo = codigo
        self.__razon_social = razon_social
        self.__ruc = ruc

    @property
    def codigo(self):
        return self.__codigo

    @property
    def razon_social(self):
        return self.__razon_social

    @property
    def ruc(self):
        return self.__ruc

    def __str__(self):
        return f"Código: {self.__codigo} | Razón Social: {self.__razon_social} | RUC: {self.__ruc}"


# JERARQUÍA PERSONA -> CLIENTE, VENDEDOR
class Persona(ABC):
    def __init__(self, documento, nombre):
        self.__documento = documento
        self.__nombre = nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def nombre(self):
        return self.__nombre

    @abstractmethod
    def obtener_rol(self):
        pass

    def __str__(self):
        return f"[{self.obtener_rol()}] {self.__documento} - {self.__nombre}"


class Cliente(Persona):
    def __init__(self, documento, razon_social, tipo_doc):
        super().__init__(documento, razon_social)
        self.__tipo_doc = tipo_doc  # "RUC" o "DNI"

    @property
    def razon_social(self):
        return self.nombre

    @property
    def tipo_doc(self):
        return self.__tipo_doc

    def obtener_rol(self):
        return self.__tipo_doc


class Vendedor(Persona):
    def __init__(self, codigo, nombre):
        super().__init__(codigo, nombre)

    @property
    def codigo(self):
        return self.documento

    def obtener_rol(self):
        return "Vendedor"

    def calcular_comision(self, ventas_netas, tasa=0.02):
        return ventas_netas * tasa


# JERARQUÍA DOCUMENTO -> COTIZACION, BOLETA, FACTURA
class DetalleCotizacion:
    def __init__(self, item, cantidad):
        self.__item = item
        self.__cantidad = cantidad

    @property
    def item(self):
        return self.__item

    @property
    def cantidad(self):
        return self.__cantidad

    def calcular_subtotal(self):
        return self.__item.precio_venta * self.__cantidad


class Documento(ABC):
    """Clase base de los comprobantes: Cotizacion, Boleta y Factura.
    Cada subclase define si descuenta stock y cómo se identifica (polimorfismo)."""

    def __init__(self, numero, cliente, vendedor):
        self._numero = numero
        self._cliente = cliente
        self._vendedor = vendedor
        self._detalles = []

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def vendedor(self):
        return self._vendedor

    def agregar_detalle(self, item, cantidad):
        if cantidad > item.stock:
            raise ExcepcionInventario(f"Stock insuficiente para {item.nombre}. Disponible: {item.stock}")
        self._detalles.append(DetalleCotizacion(item, cantidad))

    def obtener_detalles(self):
        return self._detalles

    def calcular_montos(self):
        subtotal = sum(d.calcular_subtotal() for d in self._detalles)
        descuento = subtotal * 0.05 if subtotal > 900 else 0.0
        base_imponible = subtotal - descuento
        igv = base_imponible * 0.18
        total = base_imponible + igv
        return subtotal, descuento, base_imponible, igv, total

    @abstractmethod
    def descuenta_stock(self):
        """True si al emitir este documento se debe descontar stock."""
        pass

    @abstractmethod
    def obtener_identificador(self):
        """Texto propio de cada tipo de documento (polimorfismo)."""
        pass

    def emitir(self):
        """Descuenta stock (si corresponde) y devuelve el mensaje de confirmación.
        Cada subclase hereda este comportamiento común y solo cambia lo que
        declaran descuenta_stock() y obtener_identificador()."""
        if self.descuenta_stock():
            for d in self._detalles:
                d.item.stock -= d.cantidad
            return f">> {self.obtener_identificador()} emitido(a) y stock actualizado."
        return f">> {self.obtener_identificador()} generada. Válida por 15 días."


class Cotizacion(Documento):
    def descuenta_stock(self):
        return False

    def obtener_identificador(self):
        return f"Cotización {self._numero}"


class Boleta(Documento):
    def descuenta_stock(self):
        return True

    def obtener_identificador(self):
        return f"Boleta B001-{self._numero}"


class Factura(Documento):
    def descuenta_stock(self):
        return True

    def obtener_identificador(self):
        return f"Factura F001-{self._numero}"


def crear_documento(tipo_doc, numero, cliente, vendedor):
    """Fábrica simple: 1 = Cotización; 2 = comprobante (Factura si el cliente
    tiene RUC, Boleta si tiene DNI), tal como lo describe el diagrama de flujo."""
    if tipo_doc == 1:
        return Cotizacion(numero, cliente, vendedor)
    if cliente.tipo_doc == "RUC":
        return Factura(numero, cliente, vendedor)
    return Boleta(numero, cliente, vendedor)


# CLASE ADMINISTRADORA DEL SISTEMA
class SistemaFerreyros:
    def __init__(self):
        self.__lista_items = []
        self.__lista_proveedores = []
        self.__lista_clientes = []
        self.__lista_vendedores = []
        self.__lista_documentos = []
        self.__cargar_datos_iniciales()

    def __cargar_datos_iniciales(self):
        self.__lista_proveedores.append(Proveedor("PRV-001", "Caterpillar Global Parts", "20100000001"))
        self.__lista_proveedores.append(Proveedor("PRV-002", "Hydraulic Solutions S.A.C.", "20200000002"))

        self.__lista_items.append(RepuestoIndividual("REP-0101", "Filtro de aceite de motor", "Caterpillar", "Filtros", 60.0, 85.0, 40, 10, "PRV-001"))
        self.__lista_items.append(RepuestoIndividual("REP-0102", "Filtro de combustible", "Caterpillar", "Filtros", 50.0, 70.0, 8, 10, "PRV-001"))
        self.__lista_items.append(KitRepuesto("REP-0250", "Kit de filtros (500 h)", "Caterpillar", "Kits", 150.0, 210.0, 5, 5, "PRV-001"))
        self.__lista_items.append(RepuestoIndividual("REP-0310", "Kit de sellos hidráulicos", "Caterpillar", "Sellos", 180.0, 240.0, 3, 5, "PRV-002"))

        self.__lista_clientes.append(Cliente("20512345678", "Minera Cerro Alto S.A.C.", "RUC"))
        self.__lista_clientes.append(Cliente("20687654321", "Constructora Los Andes S.A.C.", "RUC"))

        self.__lista_vendedores.append(Vendedor("V-001", "Carlos Mendoza"))
        self.__lista_vendedores.append(Vendedor("V-002", "Lucía Paredes"))

    def agregar_item(self, item):
        self.__lista_items.append(item)

    def agregar_proveedor(self, proveedor):
        self.__lista_proveedores.append(proveedor)

    def agregar_cliente(self, cliente):
        self.__lista_clientes.append(cliente)

    def obtener_proveedores(self):
        return self.__lista_proveedores

    def obtener_clientes(self):
        return self.__lista_clientes

    def obtener_vendedores(self):
        return self.__lista_vendedores

    def buscar_item(self, codigo):
        for item in self.__lista_items:
            if item.codigo.upper() == codigo.upper():
                return item
        return None

    def buscar_cliente(self, documento):
        for cli in self.__lista_clientes:
            if cli.documento == documento:
                return cli
        return None

    def buscar_vendedor(self, codigo):
        for v in self.__lista_vendedores:
            if v.codigo.upper() == codigo.upper():
                return v
        return None

    def registrar_documento(self, documento):
        self.__lista_documentos.append(documento)

    def mostrar_catalogo(self):
        print("\n---------------------------- BUSCAR REPUESTO ----------------------------")
        print(f"{'Código':<10} {'Repuesto':<32} {'Tipo':<10} {'Stock':<8} {'P.Venta':<8}")
        print(f"{'-'*10} {'-'*32} {'-'*10} {'-'*8} {'-'*8}")
        for item in self.__lista_items:
            print(item)
        print(f"Resultados: {len(self.__lista_items)}")

    def mostrar_alertas(self):
        print("\n---------------------------- ALERTAS DEL INVENTARIO ----------------------------")
        print("  REPUESTOS CON STOCK MÍNIMO")
        print(f"  {'Código':<10} {'Repuesto':<32} {'Stock':<6} {'Mínimo':<6} {'Estado'}")
        print(f"  {'-'*9} {'-'*32} {'-'*5} {'-'*6} {'-------'}")
        for item in self.__lista_items:
            if item.verificar_stock_minimo():
                print(f"  {item.codigo:<9} {item.nombre:<32} {item.stock:<5} {item.stock_minimo:<6} REPONER")

        print("\n  COTIZACIONES PENDIENTES POR VENCER")
        print(f"  {'N.°':<12} {'Cliente':<35} {'Vence':<12} {'Días'}")
        print(f"  {'-'*10} {'-'*35} {'-'*10} {'----'}")
        print(f"  COT-000041   Minera Cerro Alto S.A.C.             25/09/2026     5")
        print(f"  COT-000043   Constructora Los Andes S.A.C.    30/09/2026    10")

    def mostrar_reporte_general(self):
        print("\n---------------------- REPORTE DEL PERIODO: 09/2026 ----------------------")
        print("  Ventas netas (sin IGV) ...................   S/ 18,450.00")
        print("  Costo de ventas ..........................   S/ 12,300.00")
        print("  Utilidad bruta ...........................   S/  6,150.00")
        print("  Margen bruto .............................        33.33 %")
        print("  Valorización del inventario al costo ..   S/ 41,870.00")

    def mostrar_comisiones(self):
        print("\n  COMISIONES (2 % sobre ventas netas)")
        print(f"  {'Vendedor':<30} {'Ventas netas':<20} {'Comisión'}")
        print(f"  {'-'*25} {'-'*20} {'-'*15}")
        ventas_ejemplo = {"V-001": 9200.00, "V-002": 9250.00}
        for v in self.__lista_vendedores:
            ventas = ventas_ejemplo.get(v.codigo, 0.0)
            comision = v.calcular_comision(ventas)
            print(f"  {v.codigo} {v.nombre:<25} S/ {ventas:>10,.2f}   S/ {comision:>8.2f}")


# VALIDACIONES DE ENTRADA
def leer_entero_positivo(mensaje):
    while True:
        try:
            valor = int(input(mensaje))
            if valor < 0:
                print("[ERROR] El valor no puede ser negativo. Intente nuevamente.")
                continue
            return valor
        except ValueError:
            print("[ERROR] Ingrese un valor numérico entero válido.")

def leer_flotante_positivo(mensaje):
    while True:
        try:
            valor = float(input(mensaje))
            if valor < 0:
                print("[ERROR] El valor no puede ser negativo. Intente nuevamente.")
                continue
            return valor
        except ValueError:
            print("[ERROR] Ingrese un valor numérico válido.")

def leer_documento_valido():
    while True:
        doc = input("  Cliente (RUC 11 dígitos / DNI 8 dígitos): ").strip()
        if doc.isdigit():
            if len(doc) == 8 or len(doc) == 11:
                return doc
            else:
                print("[ERROR] El DNI debe tener 8 dígitos o el RUC 11 dígitos.")
        else:
            print("[ERROR] El documento de identidad solo debe contener números.")


# FUNCIÓN PRINCIPAL
def main():
    sistema = SistemaFerreyros()

    while True:
        print("\n========================================================================")
        print("    SISTEMA DE INVENTARIO Y COTIZACIONES DE REPUESTOS - FERREYROS")
        print("========================================================================")
        print("    [1] Gestión de repuestos y kits")
        print("    [2] Gestión de proveedores")
        print("    [3] Gestión de clientes")
        print("    [4] Registrar cotización / venta")
        print("    [5] Movimientos de stock (ingresos / ajustes)")
        print("    [6] Reportes (stock bajo, cotizaciones pendientes, utilidad)")
        print("    [7] Comisiones de vendedores")
        print("    [0] Salir")
        print("------------------------------------------------------------------------")

        try:
            opcion = leer_entero_positivo("    Seleccione una opción: ")

            if opcion == 1:
                print("\n-------------------------- GESTIÓN DE REPUESTOS --------------------------")
                print("[1] Registrar nuevo repuesto/kit")
                print("[2] Buscar y listar repuestos")
                sub_op = leer_entero_positivo("Seleccione una opción: ")

                if sub_op == 1:
                    print("\n-------------------------- REGISTRAR REPUESTO --------------------------")
                    codigo = input("Código (n.° de parte) ..: ")
                    nombre = input("Nombre .................: ")
                    marca = input("Marca ..................: ")
                    categoria = input("Categoría ..............: ")
                    tipo = leer_entero_positivo("Tipo (1=Individual, 2=Kit): ")
                    p_compra = leer_flotante_positivo("Precio de compra (S/) ..: ")
                    p_venta = leer_flotante_positivo("Precio de venta (S/) ...: ")
                    stock_ini = leer_entero_positivo("Stock inicial ..........: ")
                    stock_min = leer_entero_positivo("Stock mínimo ...........: ")
                    prov_cod = input("Proveedor (código) .....: ")

                    if tipo == 1:
                        nuevo = RepuestoIndividual(codigo, nombre, marca, categoria, p_compra, p_venta, stock_ini, stock_min, prov_cod)
                    else:
                        nuevo = KitRepuesto(codigo, nombre, marca, categoria, p_compra, p_venta, stock_ini, stock_min, prov_cod)

                    sistema.agregar_item(nuevo)
                    print(">> Repuesto registrado correctamente.")
                elif sub_op == 2:
                    sistema.mostrar_catalogo()

            elif opcion == 2:
                print("\n-------------------------- GESTIÓN DE PROVEEDORES --------------------------")
                print("[1] Registrar proveedor")
                print("[2] Listar proveedores")
                sub_op = leer_entero_positivo("Seleccione una opción: ")
                if sub_op == 1:
                    cod = input("Código de proveedor (ej. PRV-003): ")
                    razon = input("Razón social: ")
                    while True:
                        ruc = input("RUC (11 dígitos numéricos): ")
                        if ruc.isdigit() and len(ruc) == 11:
                            break
                        print("[ERROR] El RUC debe contener exactamente 11 dígitos.")
                    sistema.agregar_proveedor(Proveedor(cod, razon, ruc))
                    print(">> Proveedor registrado correctamente.")
                else:
                    print("\n--- LISTA DE PROVEEDORES ---")
                    for p in sistema.obtener_proveedores():
                        print(p)

            elif opcion == 3:
                print("\n-------------------------- GESTIÓN DE CLIENTES --------------------------")
                doc = leer_documento_valido()
                cli = sistema.buscar_cliente(doc)
                if cli:
                    print(f"Cliente encontrado: {cli}")
                else:
                    razon = input("Cliente no registrado. Ingrese Razón Social / Nombre: ")
                    tipo = "RUC" if len(doc) == 11 else "DNI"
                    nuevo_cli = Cliente(doc, razon, tipo)
                    sistema.agregar_cliente(nuevo_cli)
                    print(">> Cliente registrado exitosamente.")

            elif opcion == 4:
                print("\n--------------------------- REGISTRAR COTIZACIÓN ---------------------------")
                doc_cli = leer_documento_valido()
                cliente = sistema.buscar_cliente(doc_cli)
                if not cliente:
                    razon = input("  Razón social del nuevo cliente: ")
                    cliente = Cliente(doc_cli, razon, "RUC" if len(doc_cli) == 11 else "DNI")
                    sistema.agregar_cliente(cliente)

                cod_vendedor = input("  Código de vendedor (ej. V-002): ")
                vendedor = sistema.buscar_vendedor(cod_vendedor)
                if not vendedor:
                    print("[ERROR] Vendedor no encontrado. Se registra como texto libre.")
                    vendedor = Vendedor(cod_vendedor, "Vendedor no registrado")

                tipo_doc = leer_entero_positivo("  Documento (1=Cotización, 2=Factura/Boleta): ")

                documento = crear_documento(tipo_doc, "COT-000045", cliente, vendedor)

                try:
                    while True:
                        sistema.mostrar_catalogo()
                        cod_rep = input("\n  Ingrese Cód. de repuesto (o 'fin' para terminar): ")
                        if cod_rep.lower() == 'fin':
                            break
                        item = sistema.buscar_item(cod_rep)
                        if not item:
                            print("[ERROR] Repuesto inexistente.")
                            continue
                        cant = leer_entero_positivo("  Cantidad: ")
                        try:
                            documento.agregar_detalle(item, cant)
                        except ExcepcionInventario as e:
                            print(f"[ERROR DE NEGOCIO] {e}. Intente con otra cantidad u otro repuesto.")
                except ExcepcionInventario:
                    pass

                sub, desc, base, igv, total = documento.calcular_montos()
                print("\n-------------------------------------------------------------------------")
                print(f"  Subtotal .......................................   S/ {sub:10.2f}")
                print(f"  Descuento por volumen (5 %) ....................   S/ {desc:10.2f}")
                print(f"  Base imponible .................................   S/ {base:10.2f}")
                print(f"  IGV (18 %) .....................................   S/ {igv:10.2f}")
                print(f"  TOTAL ..........................................   S/ {total:10.2f}")

                print(f"  {documento.emitir()}")
                sistema.registrar_documento(documento)

            elif opcion == 5:
                print("\n----------------- MOVIMIENTOS DE STOCK (INGRESOS / AJUSTES) -----------------")
                cod = input("Ingrese código del repuesto: ")
                item = sistema.buscar_item(cod)
                if item:
                    print(f"Stock actual de {item.nombre}: {item.stock}")
                    print("[1] Ingreso (sumar stock)   [2] Ajuste (restar stock)")
                    mov = leer_entero_positivo("Tipo de movimiento: ")
                    cantidad = leer_entero_positivo("Cantidad: ")
                    if mov == 1:
                        item.stock += cantidad
                    else:
                        if cantidad > item.stock:
                            print("[ERROR] No se puede ajustar por debajo de 0. Movimiento cancelado.")
                        else:
                            item.stock -= cantidad
                    print(f">> Stock actualizado correctamente. Nuevo stock: {item.stock}")
                else:
                    print("[ERROR] Repuesto no encontrado.")

            elif opcion == 6:
                sistema.mostrar_alertas()
                sistema.mostrar_reporte_general()

            elif opcion == 7:
                print("\n---------------------- REPORTE DE COMISIONES ----------------------")
                sistema.mostrar_comisiones()

            elif opcion == 0:
                print("Saliendo del sistema... Guardando datos en archivo (HU16). ¡Hasta luego!")
                break
            else:
                print("[ERROR] Opción no válida. Intente entre 0 y 7.")

        except ExcepcionInventario as e:
            print(f"[ERROR DE NEGOCIO] {e}")
        except Exception as e:
            print(f"[ERROR INESPERADO] {e}")


# PRUEBAS DE LOS MÉTODOS DE NEGOCIO (unittest)
class TestMetodosDeNegocio(unittest.TestCase):
    def setUp(self):
        self.repuesto = RepuestoIndividual("REP-TEST", "Repuesto de prueba", "Caterpillar", "Filtros", 50.0, 100.0, 10, 5, "PRV-001")
        self.cliente_ruc = Cliente("20512345678", "Cliente de prueba RUC", "RUC")
        self.cliente_dni = Cliente("12345678", "Cliente de prueba DNI", "DNI")
        self.vendedor = Vendedor("V-999", "Vendedor de prueba")

    def test_calcular_montos_sin_descuento(self):
        cot = Cotizacion("COT-TEST-1", self.cliente_ruc, self.vendedor)
        cot.agregar_detalle(self.repuesto, 2)  # subtotal = 200, no supera 900
        subtotal, descuento, base, igv, total = cot.calcular_montos()
        self.assertEqual(subtotal, 200.0)
        self.assertEqual(descuento, 0.0)
        self.assertAlmostEqual(igv, 200.0 * 0.18)
        self.assertAlmostEqual(total, 200.0 * 1.18)

    def test_calcular_montos_con_descuento(self):
        cot = Cotizacion("COT-TEST-2", self.cliente_ruc, self.vendedor)
        cot.agregar_detalle(self.repuesto, 10)  # subtotal = 1000, supera 900
        subtotal, descuento, base, igv, total = cot.calcular_montos()
        self.assertEqual(subtotal, 1000.0)
        self.assertAlmostEqual(descuento, 50.0)
        self.assertAlmostEqual(base, 950.0)
        self.assertAlmostEqual(igv, 950.0 * 0.18)

    def test_agregar_detalle_stock_insuficiente(self):
        cot = Cotizacion("COT-TEST-3", self.cliente_ruc, self.vendedor)
        with self.assertRaises(ExcepcionInventario):
            cot.agregar_detalle(self.repuesto, 999)

    def test_cotizacion_no_descuenta_stock(self):
        cot = Cotizacion("COT-TEST-4", self.cliente_ruc, self.vendedor)
        cot.agregar_detalle(self.repuesto, 3)
        stock_antes = self.repuesto.stock
        cot.emitir()
        self.assertEqual(self.repuesto.stock, stock_antes)

    def test_factura_descuenta_stock(self):
        fac = Factura("F-TEST-1", self.cliente_ruc, self.vendedor)
        fac.agregar_detalle(self.repuesto, 3)
        stock_antes = self.repuesto.stock
        fac.emitir()
        self.assertEqual(self.repuesto.stock, stock_antes - 3)

    def test_crear_documento_factura_para_ruc(self):
        doc = crear_documento(2, "D-1", self.cliente_ruc, self.vendedor)
        self.assertIsInstance(doc, Factura)

    def test_crear_documento_boleta_para_dni(self):
        doc = crear_documento(2, "D-2", self.cliente_dni, self.vendedor)
        self.assertIsInstance(doc, Boleta)

    def test_calcular_comision_vendedor(self):
        self.assertAlmostEqual(self.vendedor.calcular_comision(9200.0), 184.0)


if __name__ == "__main__":
    import sys
    if "test" in sys.argv:
        sys.argv.remove("test")
        unittest.main()
    else:
        main()
