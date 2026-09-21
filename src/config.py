"""Reglas de negocio configurables del sistema (sección D.3 del informe)."""

# Impuesto General a las Ventas
IGV = 0.18

# Descuento por volumen
UMBRAL_DESCUENTO = 900.00   # S/ a partir del cual aplica el descuento
TASA_DESCUENTO = 0.05       # 5 %

# Comisión del vendedor sobre ventas netas
TASA_COMISION = 0.02        # 2 %

# Vigencia de una cotización
DIAS_VALIDEZ_COTIZACION = 15

# Descuento propio de un kit respecto a la suma de sus componentes
DESCUENTO_KIT = 0.10        # 10 %

MONEDA = "S/"
ARCHIVO_DATOS = "datos/datos.json"
