"""Pruebas automatizadas: verifican resultados y no solo ausencia de errores."""
import unittest  # Biblioteca estándar para organizar y ejecutar pruebas.
from decimal import Decimal  # Permite comparar importes exactos.
from modelos import Entidad, Servicio, Cliente, Sala, Equipo, Asesoria, Reserva  # Clases bajo prueba.
from excepciones import DatosInvalidos, OperacionNoPermitida, CalculoInvalido  # Errores esperados.
from sistema import Sistema  # Gestor de listas y reglas compartidas.


class PruebasSistema(unittest.TestCase):  # Cada método test_ representa una prueba independiente.
    def setUp(self):  # Se ejecuta antes de cada prueba para evitar dependencia entre ellas.
        self.s = Sistema()  # Crea un sistema nuevo.
        self.c = self.s.registrar_cliente('C1', 'Ana', 'ana@example.com', '3001234567')  # Cliente base.
        self.sala = self.s.registrar_servicio(Sala('S1', 'Sala', 50000))  # Servicio base.

    def test_abstractas(self):  # Verifica que las clases abstractas no se instancien.
        with self.assertRaises(TypeError):  # Espera un error de tipo de Python.
            Entidad('E1')  # Falta implementar describir.
        with self.assertRaises(TypeError):  # Verifica el contrato de Servicio.
            Servicio('S', 'Genérico', 1)  # Faltan métodos abstractos.

    def test_costos(self):  # Comprueba las tres fórmulas y las variantes de argumentos.
        self.assertEqual(self.sala.calcular_costo(2), Decimal('100000.00'))  # Sin extras.
        self.assertEqual(self.sala.calcular_costo(2, 19, 10), Decimal('107100.00'))  # Con impuesto y descuento.
        self.assertEqual(Equipo('S2', 'Equipo', 30000).calcular_costo(3), Decimal('105000.00'))  # Cargo fijo.
        self.assertEqual(Asesoria('S3', 'Asesoría', 80000).calcular_costo(4, 19), Decimal('342720.00'))  # Rebaja por duración.

    def test_datos_invalidos(self):  # Valida correos, teléfonos y cantidades no finitas.
        with self.assertRaises(DatosInvalidos):  # Espera un rechazo controlado.
            Cliente('C2', 'Ana', 'mal', '3001234567')  # Correo incorrecto.
        with self.assertRaises(DatosInvalidos):  # Comprueba el teléfono.
            Cliente('C2', 'Ana', 'a@example.com', 'abc')  # Teléfono incorrecto.
        with self.assertRaises(DatosInvalidos):  # Comprueba que NaN no sea aceptado.
            self.sala.calcular_costo('NaN')  # Duración no finita.

    def test_encadenamiento(self):  # Comprueba que se preserve la excepción original.
        with self.assertRaises(DatosInvalidos) as captura:  # captura contiene el error del negocio.
            self.sala.calcular_costo('dos')  # Provoca fallo de conversión.
        self.assertIsNotNone(captura.exception.__cause__)  # Verifica la presencia de la causa original.

    def test_estado_atomico(self):  # Confirma que un cálculo inválido no corrompe una reserva.
        r = self.s.crear_reserva('R1', 'C1', 'S1', 2)  # Reserva pendiente.
        with self.assertRaises(CalculoInvalido):  # Espera rechazo del porcentaje.
            self.s.confirmar_reserva('R1', descuento=101)  # Intenta confirmar incorrectamente.
        self.assertEqual(r.estado, 'PENDIENTE')  # Comprueba que conserva el estado original.
        self.assertIsNone(r.total)  # Comprueba que el importe sigue ausente.
        self.s.confirmar_reserva('R1')  # Reintenta con valores válidos.
        self.assertEqual(r.estado, 'CONFIRMADA')  # Comprueba transición correcta.

    def test_ocupacion(self):  # Comprueba exclusividad y liberación del servicio.
        self.s.crear_reserva('R1', 'C1', 'S1', 1)  # Primera solicitud.
        self.s.crear_reserva('R2', 'C1', 'S1', 2)  # Segunda solicitud.
        self.s.confirmar_reserva('R1')  # Ocupa la sala.
        with self.assertRaises(OperacionNoPermitida):  # Espera bloqueo de la segunda confirmación.
            self.s.confirmar_reserva('R2')  # No puede ocupar el mismo servicio.
        self.s.cancelar_reserva('R1')  # Libera la sala.
        self.assertEqual(self.s.confirmar_reserva('R2'), Decimal('100000.00'))  # Ahora resulta válida.

    def test_disponibilidad(self):  # Verifica cambios de disponibilidad antes de confirmar.
        r = self.s.crear_reserva('R1', 'C1', 'S1', 1)  # Reserva mientras está disponible.
        self.s.cambiar_disponibilidad('S1', False)  # Desactiva el servicio.
        with self.assertRaises(OperacionNoPermitida):  # Espera un rechazo.
            self.s.confirmar_reserva('R1')  # Impide confirmar después de desactivación.
        self.assertEqual(r.estado, 'PENDIENTE')  # Conserva el estado.

    def test_duplicado_y_encapsulacion(self):  # Comprueba unicidad y propiedades de lectura.
        with self.assertRaises(OperacionNoPermitida):  # Espera rechazo del código repetido.
            self.s.registrar_cliente('C1', 'Luis', 'luis@example.com', '3011234567')  # Código existente.
        with self.assertRaises(AttributeError):  # La propiedad no tiene setter.
            self.c.correo = 'nuevo@example.com'  # Intenta modificar el correo directamente.


if __name__ == '__main__':  # Permite ejecutar este archivo directamente.
    unittest.main()  # Inicia el descubrimiento de pruebas.
