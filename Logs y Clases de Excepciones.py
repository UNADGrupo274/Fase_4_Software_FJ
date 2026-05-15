# Fase 4 - Componente Práctico

import logging
from abc import ABC, abstractmethod

# ===========================================
# CONFIGURACIÓN DE LOGS (Issue #3 - Cerrado)
# ===========================================
logging.basicConfig(
    filename='Errores.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# =====================================
# ISSUE #1: EXCEPCIONES PERSONALIZADAS
# =====================================
class SoftwareFJError(Exception):
    "Clase base para excepciones del sistema Software FJ"
    pass

class ValidacionClienteError(SoftwareFJError):
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    pass

class ReservaInvalidaError(SoftwareFJError):
    pass