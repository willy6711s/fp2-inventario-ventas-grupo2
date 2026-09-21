"""Movimientos de stock: ingresos, salidas y ajustes (HU09)."""

from datetime import date

from src.excepciones import DatoInvalidoError
from src.utils.validaciones import validar_entero, validar_texto

TIPOS = ("INGRESO", "SALIDA", "AJUSTE")


class MovimientoStock:
    def __init__(self, codigo_repuesto, tipo, cantidad, motivo="",
                 fecha=None, documento=""):
        tipo = str(tipo).strip().upper()
        if tipo not in TIPOS:
            raise DatoInvalidoError(f"Tipo de movimiento inválido: {tipo}.")
        self.codigo_repuesto = str(codigo_repuesto).strip().upper()
        self.tipo = tipo
        self.cantidad = validar_entero(cantidad, "cantidad", 0)
        self.motivo = validar_texto(motivo or tipo.title(), "motivo", minimo=3)
        self.fecha = fecha or date.today()
        self.documento = documento

    def __str__(self):
        return (
            f"{self.fecha.strftime('%d/%m/%Y')} | {self.tipo:<8} | "
            f"{self.codigo_repuesto:<10} | {self.cantidad:>5} | {self.motivo}"
        )

    def to_dict(self):
        return {
            "codigo_repuesto": self.codigo_repuesto,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "motivo": self.motivo,
            "fecha": self.fecha.isoformat(),
            "documento": self.documento,
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(
            datos["codigo_repuesto"], datos["tipo"], datos["cantidad"],
            datos.get("motivo", ""), date.fromisoformat(datos["fecha"]),
            datos.get("documento", ""),
        )
