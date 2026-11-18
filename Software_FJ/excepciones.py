"""Errores propios del negocio, diferenciados de fallos de Python."""
class ErrorSistema(Exception):  # Base común para capturar errores previstos.
    pass  # Hereda el comportamiento de Exception sin modificarlo.

class DatosInvalidos(ErrorSistema):  # Datos ausentes, inválidos o fuera de rango.
    pass  # Permite distinguir este tipo de error.

class OperacionNoPermitida(ErrorSistema):  # Estado, duplicado o disponibilidad incorrectos.
    pass  # Conserva el mensaje original.

class CalculoInvalido(ErrorSistema):  # Error al calcular un importe.
    pass  # Permite identificar fallos monetarios.
