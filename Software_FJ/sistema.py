"""Gestión de listas internas y control centralizado de operaciones."""
import logging  # Biblioteca estándar para registrar eventos y errores.
from pathlib import Path  # Gestiona rutas compatibles con varios sistemas operativos.
from excepciones import ErrorSistema, DatosInvalidos, OperacionNoPermitida  # Errores controlados.
from modelos import Cliente, Servicio, Reserva  # Entidades necesarias para administrar el sistema.


def configurar_log():  # Prepara el archivo de auditoría al iniciar el programa.
    logger = logging.getLogger('software_fj')  # logger: objeto responsable de escribir eventos.
    logger.setLevel(logging.INFO)  # Registra información, advertencias y errores.
    logger.propagate = False  # Evita que los mensajes se dupliquen en el logger raíz.
    if not logger.handlers:  # Configura los destinos una sola vez por proceso.
        formato = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')  # Fecha, nivel y detalle.
        try:  # Intenta abrir el archivo de auditoría junto al código.
            archivo = logging.FileHandler(Path(__file__).with_name('eventos.log'), encoding='utf-8')  # Abre en modo anexar.
        except OSError as error:  # Controla permisos insuficientes o problemas de disco.
            archivo = logging.StreamHandler()  # Usa consola como respaldo si no puede escribir en disco.
            print(f'Advertencia: no se pudo abrir el log: {error}')  # Hace visible la limitación de auditoría.
        archivo.setFormatter(formato)  # Asigna la estructura de cada línea.
        logger.addHandler(archivo)  # Habilita el destino correspondiente.
    return logger  # Devuelve el registrador configurado.


class Sistema:  # Centraliza reglas que involucran varios objetos.
    def __init__(self):  # Inicializa una sesión sin base de datos.
        self.__clientes = []  # Lista privada de objetos Cliente.
        self.__servicios = []  # Lista privada de objetos Servicio.
        self.__reservas = []  # Lista privada de objetos Reserva.
        self.log = configurar_log()  # Registrador compartido de eventos de la sesión.

    def _buscar(self, lista, codigo):  # lista: colección a consultar; codigo: identificador buscado.
        for objeto in lista:  # Recorre cada elemento de la colección.
            if objeto.codigo == codigo:  # Compara los identificadores exactos.
                return objeto  # Retorna la referencia encontrada.
        raise DatosInvalidos(f'No existe el código {codigo}.')  # Informa que faltan datos registrados.

    def _agregar(self, lista, objeto):  # Inserta un objeto si su código no está repetido.
        if any(item.codigo == objeto.codigo for item in lista):  # any detecta al menos una coincidencia.
            raise OperacionNoPermitida(f'Código duplicado: {objeto.codigo}.')  # Impide duplicados.
        lista.append(objeto)  # Modifica la lista solo después de validar.
        return objeto  # Devuelve el objeto agregado.

    def registrar_cliente(self, codigo, nombre, correo, telefono):  # Recibe los datos de un nuevo cliente.
        cliente = Cliente(codigo, nombre, correo, telefono)  # Construye y valida antes de insertar.
        if any(c.correo == cliente.correo for c in self.__clientes):  # Busca correos repetidos.
            raise OperacionNoPermitida('Correo ya registrado.')  # Protege la unicidad del cliente.
        return self._agregar(self.__clientes, cliente)  # Agrega a la lista de clientes.

    def registrar_servicio(self, servicio):  # Recibe una instancia especializada de Servicio.
        if not isinstance(servicio, Servicio):  # Comprueba el contrato común.
            raise DatosInvalidos('El objeto debe ser un Servicio.')  # Rechaza tipos ajenos.
        return self._agregar(self.__servicios, servicio)  # Guarda en una sola lista polimórfica.

    def crear_reserva(self, codigo, cliente, servicio, duracion):  # cliente y servicio son códigos registrados.
        c = self._buscar(self.__clientes, cliente)  # c: objeto Cliente encontrado.
        s = self._buscar(self.__servicios, servicio)  # s: objeto Servicio encontrado.
        reserva = Reserva(codigo, c, s, duracion)  # Construye una reserva pendiente validada.
        return self._agregar(self.__reservas, reserva)  # Almacena solo si el código es único.

    def confirmar_reserva(self, codigo, impuesto=0, descuento=0):  # Busca y confirma aplicando regla de ocupación.
        reserva = self._buscar(self.__reservas, codigo)  # Obtiene la reserva existente.
        if any(r is not reserva and r.servicio is reserva.servicio and r.estado == 'CONFIRMADA' for r in self.__reservas):  # Detecta otra confirmación del mismo servicio.
            raise OperacionNoPermitida('Servicio ocupado por otra reserva confirmada.')  # Modelo sin calendario: una confirmación activa por servicio.
        return reserva.confirmar(impuesto, descuento)  # Confirma después de verificar ocupación.

    def cancelar_reserva(self, codigo):  # Solicita cancelación por identificador.
        reserva = self._buscar(self.__reservas, codigo)  # Recupera el objeto registrado.
        reserva.cancelar()  # Ejecuta la transición protegida.
        return reserva  # Devuelve la reserva actualizada.

    def cambiar_disponibilidad(self, codigo, estado):  # Modifica la disponibilidad administrativa.
        servicio = self._buscar(self.__servicios, codigo)  # Localiza el servicio solicitado.
        servicio.cambiar_disponibilidad(estado)  # Delega la validación booleana.
        return servicio  # Retorna el servicio actualizado.

    def listar(self):  # Expone una vista textual sin entregar las listas privadas.
        for titulo, lista in (('CLIENTES', self.__clientes), ('SERVICIOS', self.__servicios), ('RESERVAS', self.__reservas)):  # Agrupa las tres colecciones.
            print(f'\n{titulo}')  # Muestra el encabezado del grupo.
            for objeto in lista:  # Recorre objetos de diferentes clases.
                print(objeto.describir())  # Ejecuta el método sobrescrito correspondiente.

    def ejecutar(self, nombre, accion):  # nombre: etiqueta; accion: función sin argumentos que se ejecutará.
        try:  # Aísla cada operación para que un fallo no detenga la siguiente.
            resultado = accion()  # Ejecuta el registro, reserva o cálculo solicitado.
        except ErrorSistema as error:  # Captura excepciones de negocio previstas.
            self.log.exception('ERROR | %s | %s', nombre, error)  # Guarda mensaje y traza, incluido encadenamiento.
            print(f'ERROR | {nombre}: {error}')  # Presenta una explicación al usuario.
            return False, None  # Informa fallo controlado al simulador.
        except Exception as error:  # Captura errores inesperados de ejecución, sin interceptar KeyboardInterrupt.
            self.log.exception('INESPERADO | %s', nombre)  # Registra diagnóstico técnico.
            print(f'ERROR inesperado | {nombre}: {error}')  # Comunica el fallo sin cerrar la aplicación.
            return False, None  # Permite continuar con la siguiente operación.
        else:  # Solo se ejecuta si el bloque try no lanzó excepciones.
            detalle = resultado.describir() if hasattr(resultado, 'describir') else str(resultado)  # Prepara una respuesta legible.
            self.log.info('OK | %s | %s', nombre, detalle)  # Registra el evento exitoso.
            print(f'OK | {nombre}: {detalle}')  # Muestra el resultado.
            return True, resultado  # Informa éxito y entrega el objeto o importe.
        finally:  # Se ejecuta tanto en éxito como en error.
            self.log.info('FIN | %s', nombre)  # Deja evidencia del cierre de cada intento.
