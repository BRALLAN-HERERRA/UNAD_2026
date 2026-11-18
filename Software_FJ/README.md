# Software FJ – Fase 4 | Programación 213023

Proyecto de referencia para la práctica colaborativa de la UNAD. Sistema integral de gestión de clientes, servicios y reservas. Python 3.10 o superior (recomendado 3.12), sin dependencias externas ni bases de datos.

## Ejecutar

1. Instalar Python desde https://www.python.org/downloads/.
2. Abrir la carpeta Software_FJ en Visual Studio Code o una terminal.
3. Ejecutar `python main.py` (en Windows también `py main.py`).
4. Ejecutar `python -m unittest -v` para las pruebas de comportamiento.
5. Abrir `eventos.log` para revisar eventos y trazas. El archivo se amplía en cada ejecución. Los datos del negocio se pierden al finalizar, deliberadamente.

## Organización y flujo

- `excepciones.py`: jerarquía de errores personalizados.
- `modelos.py`: funciones de validación y entidades abstractas y concretas.
- `sistema.py`: listas internas, búsquedas, reglas de ocupación y registro de eventos.
- `main.py`: demostración automática de 28 operaciones, con expectativa de éxito o fallo por caso.
- `test_sistema.py`: pruebas unitarias de reglas y costos.
- `eventos.log`: evidencia auténtica generada al ejecutar el código.
- `GUIA_TECNICA.md`: explicación de clases, variables, condiciones y publicación en GitHub.

Flujo: main → Sistema.ejecutar → operación de negocio → validación/modelos → resultado o excepción → log → siguiente operación. El procesamiento de una reserva calcula el costo; la confirmación fija el valor y cambia el estado. La cancelación libera el servicio.

## Reglas de diseño propuestas

Los límites de duración, tarifas y porcentajes son ejemplos ficticios elegidos para la simulación, no valores definidos por la UNAD ni tasas fiscales reales. No se modelan fechas: un servicio solo admite una reserva confirmada a la vez. La duración puede ser decimal, entre 1 y el máximo del tipo. El impuesto y descuento son porcentajes opcionales entre 0 y 100. El archivo de logs es la única escritura persistente realizada por la aplicación; no se cargan clientes ni reservas desde él.

## Resultado comprobado

28/28 operaciones con la respuesta esperada: 17 exitosas y 11 errores controlados. Los casos negativos son parte de la demostración, no defectos pendientes. El archivo de auditoría contiene trazas de errores y eventos OK/FIN. Los casos son ficticios y no constituyen evidencia de participación de los integrantes.

## Participación académica

Subir al repositorio asignado por el docente; cada integrante debe revisar, ejecutar, comprender y aportar cambios reales mediante commits propios. Completar la portada y el enlace auténtico en el informe. Este proyecto no se ha publicado en GitHub desde aquí. Reconocer el apoyo de IA de acuerdo con las indicaciones del curso.
