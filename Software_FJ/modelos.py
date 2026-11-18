"""Entidades del negocio: clientes, servicios y reservas en memoria."""
from abc import ABC, abstractmethod  # Herramientas para definir contratos abstractos.
from decimal import Decimal, InvalidOperation  # Aritmética monetaria exacta y su excepción.
import re  # Valida formatos de texto mediante expresiones regulares.
from excepciones import DatosInvalidos, OperacionNoPermitida, CalculoInvalido  # Errores del negocio.


def texto(valor, campo):  # valor: dato recibido; campo: nombre para el mensaje de error.
    if not isinstance(valor, str) or not valor.strip():  # Rechaza tipos incorrectos y espacios vacíos.
        raise DatosInvalidos(f'{campo} es obligatorio y debe ser texto.')  # Interrumpe solo esta operación.
    return valor.strip()  # Elimina espacios exteriores sin alterar el contenido interno.


def numero(valor, campo, minimo=0):  # minimo: límite inferior permitido, incluido.
    try:  # Intenta convertir datos escritos por el usuario.
        n = Decimal(str(valor))  # n: número decimal convertido sin redondeo binario.
    except (InvalidOperation, ValueError, TypeError) as error:  # Captura conversiones fallidas.
        raise DatosInvalidos(f'{campo} debe ser numérico.') from error  # Conserva la causa original.
    if not n.is_finite() or n < minimo:  # Rechaza infinito, NaN y valores menores al límite.
        raise DatosInvalidos(f'{campo} debe ser finito y mayor o igual a {minimo}.')  # Explica el límite.
    return n  # Entrega un decimal validado.


class Entidad(ABC):  # Clase abstracta común a los objetos identificables.
    def __init__(self, codigo):  # self representa la instancia actual; codigo identifica el objeto.
        self.__codigo = texto(codigo, 'Código')  # Atributo privado que protege el identificador.

    @property  # Permite consultar el código como atributo, sin modificarlo directamente.
    def codigo(self):  # Devuelve el identificador de esta instancia.
        return self.__codigo  # No se define setter para evitar cambios accidentales.

    @abstractmethod  # Obliga a las clases concretas a implementar su descripción.
    def describir(self):  # Contrato común para presentar información.
        pass  # No existe una descripción genérica concreta.


class Cliente(Entidad):  # Hereda el identificador y el contrato de Entidad.
    def __init__(self, codigo, nombre, correo, telefono):  # Datos personales del cliente.
        super().__init__(codigo)  # Reutiliza la validación del identificador.
        self.__nombre = texto(nombre, 'Nombre')  # Guarda el nombre validado de forma privada.
        correo = texto(correo, 'Correo')  # Normaliza espacios exteriores del correo.
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', correo):  # Comprueba formato básico, no existencia real.
            raise DatosInvalidos('Correo electrónico inválido.')  # Evita crear un cliente inconsistente.
        telefono = texto(telefono, 'Teléfono')  # Se conserva como texto para no perder ceros iniciales.
        if not re.fullmatch(r'\d{7,15}', telefono):  # Exige entre 7 y 15 dígitos.
            raise DatosInvalidos('Teléfono inválido: use entre 7 y 15 dígitos.')  # Informa el formato esperado.
        self.__correo = correo.lower()  # Normaliza mayúsculas para comparar correos.
        self.__telefono = telefono  # Protege el teléfono frente a asignaciones directas.

    @property  # Expone únicamente lectura del nombre.
    def nombre(self):  # Obtiene el nombre del cliente.
        return self.__nombre  # Devuelve texto inmutable.

    @property  # Permite consultar el correo validado.
    def correo(self):  # Obtiene el correo del cliente.
        return self.__correo  # No permite asignación mediante esta propiedad.

    @property  # Permite consultar el teléfono validado.
    def telefono(self):  # Obtiene el teléfono del cliente.
        return self.__telefono  # Mantiene el dato encapsulado.

    def describir(self):  # Sobrescribe el método abstracto de Entidad.
        return f'{self.codigo}: {self.nombre}'  # Omite teléfono y correo en listados y logs.


class Servicio(Entidad, ABC):  # Contrato abstracto de cualquier servicio comercial.
    def __init__(self, codigo, nombre, tarifa, disponible=True):  # tarifa: precio por hora; disponible: bandera operativa.
        super().__init__(codigo)  # Inicializa el identificador heredado.
        self.__nombre = texto(nombre, 'Servicio')  # Guarda el nombre privado.
        self.__tarifa = numero(tarifa, 'Tarifa', Decimal('0.01'))  # Exige tarifa estrictamente positiva.
        if not isinstance(disponible, bool):  # Impide confundir cadenas como "False" con verdadero.
            raise DatosInvalidos('Disponibilidad debe ser True o False.')  # Rechaza un tipo incorrecto.
        self.__disponible = disponible  # Guarda el estado de disponibilidad.

    @property  # Consulta pública de la tarifa.
    def tarifa(self):  # Retorna el precio unitario.
        return self.__tarifa  # Decimal inmutable.

    @property  # Consulta pública de la disponibilidad.
    def disponible(self):  # Indica si se puede reservar actualmente.
        return self.__disponible  # Devuelve un booleano.

    def cambiar_disponibilidad(self, estado):  # estado: nuevo valor booleano.
        if not isinstance(estado, bool):  # Valida antes de modificar el objeto.
            raise DatosInvalidos('Disponibilidad inválida.')  # El estado anterior se conserva.
        self.__disponible = estado  # Aplica el cambio válido.

    def etiqueta(self):  # Reúne los datos compartidos por las descripciones.
        return f'{self.codigo} - {self.__nombre}'  # Identificación legible.

    @abstractmethod  # Cada servicio define sus propios límites.
    def validar_parametros(self, duracion):  # duracion: horas solicitadas.
        pass  # La implementación corresponde a las subclases.

    @abstractmethod  # Cada tipo aplica su fórmula de precio base.
    def costo_base(self, duracion):  # Recibe horas ya validadas.
        pass  # No hay fórmula única para todos los servicios.

    def calcular_costo(self, duracion, impuesto=0, descuento=0):  # Sobrecarga simulada con argumentos opcionales, en porcentajes.
        horas = self.validar_parametros(duracion)  # Usa la validación polimórfica de la subclase.
        iva = numero(impuesto, 'Impuesto')  # iva: porcentaje adicional, no una tasa legal fija.
        rebaja = numero(descuento, 'Descuento')  # rebaja: porcentaje que se resta al precio.
        if iva > 100 or rebaja > 100:  # Acota ambos porcentajes al intervalo 0 a 100.
            raise CalculoInvalido('Los porcentajes no pueden superar 100.')  # Evita importes inconsistentes.
        try:  # Protege las operaciones monetarias.
            base = self.costo_base(horas)  # Despacha la fórmula de la clase concreta.
            total = base * (1 - rebaja / 100) * (1 + iva / 100)  # Descuenta primero y aplica impuesto después.
            return total.quantize(Decimal('0.01'))  # Redondea a dos decimales.
        except ArithmeticError as error:  # Incluye errores aritméticos de Decimal.
            raise CalculoInvalido('No fue posible calcular el costo.') from error  # Encadena la causa técnica.

    def _validar_horas(self, duracion, limite):  # limite: máximo de horas del servicio.
        horas = numero(duracion, 'Duración', 1)  # Exige una duración mínima de una hora.
        if horas > limite:  # Comprueba el máximo definido por cada servicio.
            raise DatosInvalidos(f'Duración máxima: {limite} horas.')  # Impide reservas fuera del rango.
        return horas  # Devuelve la duración normalizada.


class Sala(Servicio):  # Especialización para reservas de salas.
    def validar_parametros(self, duracion):  # Sobrescribe el contrato de validación.
        return self._validar_horas(duracion, 12)  # Regla simulada: máximo 12 horas.

    def costo_base(self, duracion):  # Sobrescribe la fórmula abstracta.
        return self.tarifa * duracion  # Cobra únicamente por las horas utilizadas.

    def describir(self):  # Presenta información específica de salas.
        return f'Sala: {self.etiqueta()} | {self.tarifa} COP/h'  # Texto para catálogo.


class Equipo(Servicio):  # Especialización para alquiler de equipos.
    def validar_parametros(self, duracion):  # Define los límites del alquiler.
        return self._validar_horas(duracion, 48)  # Regla simulada: máximo 48 horas.

    def costo_base(self, duracion):  # Calcula alquiler más preparación.
        return self.tarifa * duracion + Decimal('15000')  # Cargo fijo simulado de preparación.

    def describir(self):  # Identifica el tipo de servicio y su cargo adicional.
        return f'Equipo: {self.etiqueta()} | {self.tarifa} COP/h + 15000 COP'  # Describe la tarifa.


class Asesoria(Servicio):  # Especialización para asesorías profesionales.
    def validar_parametros(self, duracion):  # Define la duración de una sesión.
        return self._validar_horas(duracion, 8)  # Regla simulada: máximo 8 horas.

    def costo_base(self, duracion):  # Calcula la tarifa según duración.
        factor = Decimal('0.90') if duracion >= 4 else Decimal('1')  # Aplica 10% de rebaja desde cuatro horas.
        return self.tarifa * duracion * factor  # Retorna el precio base ajustado.

    def describir(self):  # Describe la modalidad de asesoría.
        return f'Asesoría: {self.etiqueta()} | {self.tarifa} COP/h; 10% desde 4 h'  # Informa la regla.


class Reserva(Entidad):  # Relaciona objetos Cliente y Servicio mediante composición de referencias.
    def __init__(self, codigo, cliente, servicio, duracion):  # Recibe objetos existentes y horas.
        super().__init__(codigo)  # Valida el código de la reserva.
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):  # Verifica tipos de relaciones.
            raise DatosInvalidos('Se requiere un cliente y un servicio válidos.')  # No admite referencias incorrectas.
        if not servicio.disponible:  # Comprueba disponibilidad antes de crear la reserva.
            raise OperacionNoPermitida('Servicio no disponible.')  # Evita una reserva inválida.
        self.__cliente = cliente  # Referencia privada al cliente registrado.
        self.__servicio = servicio  # Referencia privada al servicio seleccionado.
        self.__duracion = servicio.validar_parametros(duracion)  # Valida horas según el tipo de servicio.
        self.__estado = 'PENDIENTE'  # Estado inicial antes de la confirmación.
        self.__total = None  # Aún no existe un importe procesado.

    @property  # Permite consultar el estado sin asignarlo desde afuera.
    def estado(self):  # Devuelve el estado actual.
        return self.__estado  # Protege las transiciones de estado.

    @property  # Permite consultar el servicio vinculado.
    def servicio(self):  # Devuelve el objeto asociado.
        return self.__servicio  # Se usa para verificar ocupación.

    @property  # Consulta el importe fijado al confirmar.
    def total(self):  # Puede devolver None si no ha sido confirmada.
        return self.__total  # Permite verificar el resultado monetario.

    def procesar(self, impuesto=0, descuento=0):  # Calcula un importe sin cambiar estado.
        if self.estado != 'PENDIENTE':  # Solo permite calcular reservas pendientes.
            raise OperacionNoPermitida('Solo se procesan reservas pendientes.')  # Evita reprocesar reservas.
        if not self.servicio.disponible:  # Revalida disponibilidad al procesar.
            raise OperacionNoPermitida('Servicio no disponible al procesar.')  # Rechaza cambios posteriores.
        return self.servicio.calcular_costo(self.__duracion, impuesto, descuento)  # Usa despacho polimórfico.

    def confirmar(self, impuesto=0, descuento=0):  # Confirma únicamente después de calcular correctamente.
        importe = self.procesar(impuesto, descuento)  # Si falla, no cambia estado ni total.
        self.__total = importe  # Fija el costo validado.
        self.__estado = 'CONFIRMADA'  # Aplica la transición válida.
        return importe  # Entrega el valor para informar al usuario.

    def cancelar(self):  # Cancela una reserva pendiente o confirmada.
        if self.estado == 'CANCELADA':  # Evita cancelar dos veces.
            raise OperacionNoPermitida('La reserva ya está cancelada.')  # Conserva el estado actual.
        self.__estado = 'CANCELADA'  # Libera la ocupación lógica del servicio.

    def describir(self):  # Presenta el estado, cliente, servicio y costo.
        return f'{self.codigo} | {self.__cliente.codigo} | {self.servicio.codigo} | {self.__duracion} h | {self.estado} | total: {self.total}'  # Resumen de la reserva.
