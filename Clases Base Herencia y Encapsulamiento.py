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

# ==================================================
# ISSUE #2: CLASES BASE, HERENCIA Y ENCAPSULAMIENTO
# ==================================================

class EntidadGeneral(ABC):
    "Clase abstracta para entidades generales del sistema"
    @abstractmethod
    def mostrar_detalles(self):
        pass

class Cliente(EntidadGeneral):
    "Clase Cliente con encapsulación robusta"
    def __init__(self, nombre, documento, correo):
        self.__nombre = nombre
        self.__documento = documento
        self.correo = correo  # Llama al setter anterior con validación

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise ValidacionClienteError(f"Formato de correo inválido: {valor}")
        self.__correo = valor

    def mostrar_detalles(self):
        return f"Cliente: {self.__nombre} (Doc: {self.__documento})"

class Servicio(ABC):
    "Clase abstracta Servicio"
    def __init__(self, id_servicio, nombre, costo_base):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = True

    @abstractmethod
    def calcular_costo(self, impuestos=True, descuento=0):
        "Método abstracto que simula sobrecarga con parámetros opcionales"
        pass

    @abstractmethod
    def describir(self):
        pass

class ReservaSalas(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, capacidad):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacidad

    def calcular_costo(self, impuestos=True, descuento=0):
        costo = self.costo_base - descuento
        if impuestos:
            costo *= 1.19  # 19% IVA
        return costo

    def describir(self):
        return f"Sala '{self.nombre}' para {self.capacidad} personas."

class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, tipo_equipo):
        super().__init__(id_servicio, nombre, costo_base)
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, impuestos=True, descuento=0, seguro_danos=50000):
        # Sobrecarga añadiendo costo de seguro
        costo = self.costo_base - descuento + seguro_danos
        return costo * 1.19 if impuestos else costo

    def describir(self):
        return f"Equipo: {self.nombre} ({self.tipo_equipo})."

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, consultor):
        super().__init__(id_servicio, nombre, costo_base)
        self.consultor = consultor

    def calcular_costo(self, impuestos=True, descuento=0):
        # Las asesorías no cobran IVA en este ejemplo
        return self.costo_base - descuento

    def describir(self):
        return f"Asesoría en {self.nombre} por {self.consultor}."