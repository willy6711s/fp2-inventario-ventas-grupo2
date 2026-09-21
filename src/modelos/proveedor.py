"""Proveedor de repuestos (HU04)."""

from src.utils.validaciones import (
    validar_codigo,
    validar_correo,
    validar_ruc,
    validar_telefono,
    validar_texto,
)


class Proveedor:
    def __init__(self, codigo, razon_social, ruc, telefono="", correo="", contacto=""):
        self.codigo = validar_codigo(codigo)
        self.razon_social = validar_texto(razon_social, "razón social", minimo=3)
        self.ruc = validar_ruc(ruc)
        self.telefono = validar_telefono(telefono)
        self.correo = validar_correo(correo)
        self.contacto = contacto.strip() if contacto else ""
        self.activo = True

    def __str__(self):
        return f"{self.codigo} | {self.razon_social} | RUC {self.ruc}"

    def to_dict(self):
        return {
            "codigo": self.codigo,
            "razon_social": self.razon_social,
            "ruc": self.ruc,
            "telefono": self.telefono,
            "correo": self.correo,
            "contacto": self.contacto,
            "activo": self.activo,
        }

    @classmethod
    def from_dict(cls, datos):
        proveedor = cls(
            datos["codigo"],
            datos["razon_social"],
            datos["ruc"],
            datos.get("telefono", ""),
            datos.get("correo", ""),
            datos.get("contacto", ""),
        )
        proveedor.activo = datos.get("activo", True)
        return proveedor
