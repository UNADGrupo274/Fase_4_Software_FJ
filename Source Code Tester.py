# Fase 4 - Componente Práctico

import logging

# 1. Configuramos el logger para guardar los errores en un archivo llamado 'Errores.log' con un formato específico.
logging.basicConfig(
    filename='errores.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 2. Forzamos un error de prueba
try:
    print(10 / 0) # Esto va a fallar sí o sí
except ZeroDivisionError as e:
    logging.error(f"¡Prueba exitosa! Error detectado: {e}")
    print("El error se guardó en el log. Revisa el archivo errores.log")