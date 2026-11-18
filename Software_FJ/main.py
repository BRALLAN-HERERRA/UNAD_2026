"""Simulación reproducible del ejercicio de la Fase 4."""
from modelos import Sala, Equipo, Asesoria  # Importa los tres tipos concretos de servicio.
from sistema import Sistema  # Importa el gestor de objetos y excepciones.


def simular():  # Ejecuta casos positivos y negativos en orden.
    sistema = Sistema()  # Crea una sesión nueva con listas vacías.
    casos = [  # Cada tupla contiene descripción, función diferida y éxito esperado.
        ('01 Cliente válido', lambda: sistema.registrar_cliente('C1', 'Ana Pérez', 'ana@example.com', '3001234567'), True),  # Crea el primer cliente.
        ('02 Correo inválido', lambda: sistema.registrar_cliente('C2', 'Luis', 'sin-arroba', '3001234567'), False),  # Rechaza formato incorrecto.
        ('03 Cliente válido', lambda: sistema.registrar_cliente('C2', 'Luis Gómez', 'luis@example.com', '3011234567'), True),  # Demuestra recuperación.
        ('04 Cliente duplicado', lambda: sistema.registrar_cliente('C1', 'Otra persona', 'otra@example.com', '3021234567'), False),  # Comprueba código único.
        ('05 Sala válida', lambda: sistema.registrar_servicio(Sala('S1', 'Sala Norte', 50000)), True),  # Registra sala.
        ('06 Equipo válido', lambda: sistema.registrar_servicio(Equipo('S2', 'Proyector', 30000)), True),  # Registra alquiler.
        ('07 Asesoría válida', lambda: sistema.registrar_servicio(Asesoria('S3', 'Consultoría', 80000)), True),  # Registra asesoría.
        ('08 Tarifa negativa', lambda: sistema.registrar_servicio(Sala('S4', 'Sala Sur', -1)), False),  # Rechaza tarifa negativa.
        ('09 Duración no numérica', lambda: sistema.crear_reserva('R1', 'C1', 'S1', 'dos'), False),  # Demuestra encadenamiento.
        ('10 Reserva de sala', lambda: sistema.crear_reserva('R1', 'C1', 'S1', 2), True),  # Crea reserva pendiente.
        ('11 Confirmar sala', lambda: sistema.confirmar_reserva('R1', 19, 10), True),  # Total esperado: 107100 COP.
        ('12 Reserva competidora', lambda: sistema.crear_reserva('R2', 'C2', 'S1', 1), True),  # Admite solicitud pendiente.
        ('13 Confirmación ocupada', lambda: sistema.confirmar_reserva('R2'), False),  # Bloquea doble ocupación.
        ('14 Cancelar sala', lambda: sistema.cancelar_reserva('R1'), True),  # Libera la ocupación.
        ('15 Confirmar tras cancelar', lambda: sistema.confirmar_reserva('R2'), True),  # Confirma tras liberación.
        ('16 Cancelación repetida', lambda: sistema.cancelar_reserva('R1'), False),  # Impide transición inválida.
        ('17 Desactivar equipo', lambda: sistema.cambiar_disponibilidad('S2', False), True),  # Marca indisponibilidad administrativa.
        ('18 Equipo no disponible', lambda: sistema.crear_reserva('R3', 'C1', 'S2', 3), False),  # Impide reserva desactivada.
        ('19 Activar equipo', lambda: sistema.cambiar_disponibilidad('S2', True), True),  # Restaura disponibilidad.
        ('20 Reserva de equipo', lambda: sistema.crear_reserva('R3', 'C1', 'S2', 3), True),  # Crea alquiler.
        ('21 Confirmar equipo', lambda: sistema.confirmar_reserva('R3'), True),  # Total esperado: 105000 COP.
        ('22 Reserva asesoría', lambda: sistema.crear_reserva('R4', 'C2', 'S3', 4), True),  # Aplica regla de cuatro horas.
        ('23 Descuento inválido', lambda: sistema.confirmar_reserva('R4', descuento=110), False),  # No modifica el estado pendiente.
        ('24 Confirmar asesoría', lambda: sistema.confirmar_reserva('R4', impuesto=19), True),  # Total esperado: 342720 COP.
        ('25 Cliente inexistente', lambda: sistema.crear_reserva('R5', 'C9', 'S1', 1), False),  # Verifica referencias.
        ('26 Parámetro faltante', lambda: sistema.registrar_cliente('C3', 'Eva', 'eva@example.com'), False),  # Captura TypeError inesperado.
        ('27 Duración fuera del límite', lambda: sistema.crear_reserva('R5', 'C1', 'S3', 9), False),  # Valida límite específico.
        ('28 Reserva posterior al error', lambda: sistema.crear_reserva('R5', 'C1', 'S3', 1), True),  # Demuestra continuidad.
    ]  # Fin de los casos de prueba.
    aciertos = 0  # Cuenta coincidencias entre resultados reales y esperados.
    exitos = 0  # Cuenta operaciones exitosas.
    for nombre, accion, esperado in casos:  # Desempaqueta cada caso sin ejecutar los restantes anticipadamente.
        ok, resultado = sistema.ejecutar(nombre, accion)  # Ejecuta bajo control de excepciones.
        exitos += int(ok)  # Convierte True en 1 y False en 0 para contar éxitos.
        aciertos += int(ok == esperado)  # Cuenta el caso si el comportamiento fue el esperado.
        print(f'    Verificación: {"CORRECTA" if ok == esperado else "FALLIDA"}')  # Compara contra la expectativa.
    sistema.listar()  # Muestra las entidades que sobrevivieron a los errores.
    print(f'\nRESUMEN: {aciertos}/{len(casos)} casos esperados; {exitos} éxitos y {len(casos)-exitos} errores controlados.')  # Resume pruebas reales.
    return aciertos == len(casos)  # Devuelve si toda la simulación coincide con lo esperado.


if __name__ == '__main__':  # Solo ejecuta automáticamente si este archivo es el punto de entrada.
    raise SystemExit(0 if simular() else 1)  # Código de salida 0 si todas las verificaciones pasan.
