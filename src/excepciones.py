"""Excepciones propias del sistema (HU: manejo de errores, pantalla 7)."""


class ErrorSistema(Exception):
    """Excepción base de la aplicación."""


class DatoInvalidoError(ErrorSistema):
    """El dato ingresado no cumple el formato o el rango esperado."""


class StockInsuficienteError(ErrorSistema):
    """No hay unidades suficientes para atender la operación."""

    def __init__(self, codigo, solicitado, disponible):
        self.codigo = codigo
        self.solicitado = solicitado
        self.disponible = disponible
        super().__init__(
            f"Stock insuficiente para {codigo}. Solicitado: {solicitado}. Disponible: {disponible}."
        )


class EntidadNoEncontradaError(ErrorSistema):
    """El registro buscado no existe en el sistema."""


class EntidadDuplicadaError(ErrorSistema):
    """Ya existe un registro con el mismo código."""


class CotizacionVencidaError(ErrorSistema):
    """La cotización superó su fecha de validez."""


class OperacionNoPermitidaError(ErrorSistema):
    """La operación no es válida para el estado actual del registro."""
