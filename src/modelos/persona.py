"""Jerarquía Persona -> Cliente / Vendedor (herencia y polimorfismo)."""

from abc import ABC, abstractmethod

from src.excepciones import DatoInvalidoError
from src.utils.validaciones import (
    validar_codigo,
    validar_correo,
    validar_decimal,
    validar_documento_identidad,
    validar_telefono,
    validar_texto,
)


class Persona(ABC):
    """Clase base para todas las personas registradas en el sistema."""

    def __init__(self, codigo, nombre, documento, telefono="", correo=""):
        self.codigo = validar_codigo(codigo)
        self.nombre = validar_texto(nombre, "nombre", minimo=3)
        self.documento, self.tipo_documento = validar_documento_identidad(documento)
        self.telefono = validar_telefono(telefono)
        self.correo = validar_correo(correo)
        self.activo = True

    @property
    @abstractmethod
    def rol(self):
        """Rol de la persona dentro del proceso."""

    @abstractmethod
    def descripcion(self):
        """Texto descriptivo; cada subclase lo redefine (polimorfismo)."""

    def __str__(self):
        return f"{self.codigo} | {self.nombre} ({self.tipo_documento} {self.documento})"

    def to_dict(self):
        return {
            "clase": type(self).__name__,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "documento": self.documento,
            "telefono": self.telefono,
            "correo": self.correo,
            "activo": self.activo,
        }


class Cliente(Persona):
    """Cliente empresa (RUC -> factura) o persona natural (DNI -> boleta)."""

    def __init__(self, codigo, nombre, documento, telefono="", correo="", sector="General"):
        super().__init__(codigo, nombre, documento, telefono, correo)
        self.sector = validar_texto(sector, "sector", minimo=3)

    @property
    def rol(self):
        return "Cliente"

    @property
    def es_empresa(self):
        return self.tipo_documento == "RUC"

    def documento_que_corresponde(self):
        """HU08: define si se emite factura o boleta."""
        return "FACTURA" if self.es_empresa else "BOLETA"

    def descripcion(self):
        tipo = "Empresa" if self.es_empresa else "Persona natural"
        return f"{tipo} - {self.nombre} | Sector: {self.sector}"

    def to_dict(self):
        datos = super().to_dict()
        datos["sector"] = self.sector
        return datos

    @classmethod
    def from_dict(cls, datos):
        cliente = cls(
            datos["codigo"],
            datos["nombre"],
            datos["documento"],
            datos.get("telefono", ""),
            datos.get("correo", ""),
            datos.get("sector", "General"),
        )
        cliente.activo = datos.get("activo", True)
        return cliente


class Vendedor(Persona):
    """Vendedor de repuestos; genera comisión sobre sus ventas netas (HU12)."""

    def __init__(self, codigo, nombre, documento, telefono="", correo="",
                 tasa_comision=0.02, meta_mensual=0.0):
        super().__init__(codigo, nombre, documento, telefono, correo)
        self.tasa_comision = validar_decimal(tasa_comision, "tasa de comisión", 0.0, 1.0)
        self.meta_mensual = validar_decimal(meta_mensual, "meta mensual", 0.0)

    @property
    def rol(self):
        return "Vendedor"

    def calcular_comision(self, ventas_netas):
        ventas = validar_decimal(ventas_netas, "ventas netas", 0.0)
        return round(ventas * self.tasa_comision, 2)

    def cumplio_meta(self, ventas_netas):
        if self.meta_mensual <= 0:
            return None
        return ventas_netas >= self.meta_mensual

    def descripcion(self):
        return f"Vendedor {self.nombre} | Comisión {self.tasa_comision * 100:.1f} %"

    def to_dict(self):
        datos = super().to_dict()
        datos["tasa_comision"] = self.tasa_comision
        datos["meta_mensual"] = self.meta_mensual
        return datos

    @classmethod
    def from_dict(cls, datos):
        vendedor = cls(
            datos["codigo"],
            datos["nombre"],
            datos["documento"],
            datos.get("telefono", ""),
            datos.get("correo", ""),
            datos.get("tasa_comision", 0.02),
            datos.get("meta_mensual", 0.0),
        )
        vendedor.activo = datos.get("activo", True)
        return vendedor
