# Fase 4 - Componente Práctico

import logging
from abc import ABC, abstractmethod

# =============================================================
# ISSUE #3: CONFIGURACIÓN DE LOGS (Módulo logging Errores.log)
# =============================================================

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

# ==================================================
# LÓGICA DE RESERVAS (Correspondiente al simulador)
# ==================================================

class Reserva:
    def __init__(self, cliente, servicio, horas):
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "Pendiente"

    def procesar_reserva(self):
        "Aplica try/except/else/finally y encadenamiento"
        try:
            logging.info(f"Iniciando proceso de reserva para {self.cliente.mostrar_detalles()}")
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio {self.servicio.nombre} ya está ocupado.")
            if self.horas <= 0:
                raise ValueError("La cantidad de horas debe ser mayor a cero.")
            
            # Simulando un error de procesamiento interno encadenado
            if self.horas > 24:
                 try:
                     raise OverflowError("Exceso de horas permitidas")
                 except OverflowError as e:
                     raise ReservaInvalidaError("Reserva excede el límite diario") from e
            
            self.servicio.disponible = False
            self.estado = "Confirmada"
            costo_total = self.servicio.calcular_costo() * self.horas
            logging.info(f"Reserva exitosa: {self.servicio.nombre}. Total: ${costo_total:.2f}")

        except ServicioNoDisponibleError as e:
            logging.error(f"Fallo de disponibilidad: {e}")
            self.estado = "Fallida"
        except ValidacionClienteError as e:
            logging.error(f"Error de validación del cliente: {e}")
            self.estado = "Fallida"
        except ReservaInvalidaError as e:
            # Ejemplo de encadenamiento capturado
            logging.error(f"Reserva inválida: {e}. Causa original: {e.__cause__}")
            self.estado = "Fallida"
        except Exception as e:
            logging.error(f"Error inesperado procesando la reserva: {e}")
            self.estado = "Fallida"
        else:
            logging.info("El bloque try se ejecutó sin errores (Cláusula ELSE ejecutada).")
            print(f"ÉXITO: Reserva {self.estado} para {self.servicio.nombre}.")
        finally:
            logging.info(f"Finalizando transacción de reserva. Estado final: {self.estado} (Cláusula FINALLY ejecutada).")
            print("-" * 40)

# ====================================
# ISSUE #4: 10 SIMULACIONES COMPLETAS
# ====================================

def ejecutar_simulaciones():
    print("Iniciando simulaciones de Software FJ...\n") # Todos los datos son de ejemplo para demostrar la funcionalidad del sistema.
    
    # 1. Registro válido de cliente
    try:
        c1 = Cliente("Daniel Vanegas", "101010", "davanegas@unad.edu.co")
        print("1. Cliente válido creado.")
    except Exception as e:
        print(f"Error 1: {e}")

    # 2. Registro inválido de cliente (Correo malo)
    try:
        c2 = Cliente("Manuela Rosas", "202020", "correo-sin-arroba.com")
    except ValidacionClienteError as e:
        print(f"2. Excepción capturada correctamente: {e}")
        logging.error(f"Intento de creación de cliente fallido: {e}")

    # 3. Creación de Servicios válidos
    sala_juntas = ReservaSalas("S01", "Sala VIP", 100000, 15)
    proyector = AlquilerEquipos("E01", "Proyector 4K", 50000, "Audiovisual")
    asesoria_ti = AsesoriaEspecializada("A01", "Auditoría de Software", 200000, "Ing. Juan Manuel")
    print("3. Servicios creados correctamente.")

    # 4. Reserva exitosa (Sala)
    r1 = Reserva(c1, sala_juntas, 3)
    r1.procesar_reserva() # Ejecuta try/else/finally

    # 5. Falla: Servicio no disponible (Intentar reservar la misma sala)
    c3 = Cliente("Luna Galindo", "303030", "luna@unad.edu.co")
    r2 = Reserva(c3, sala_juntas, 2)
    r2.procesar_reserva()

    # 6. Reserva exitosa (Equipo) demostrando sobrecarga en cálculo
    r3 = Reserva(c1, proyector, 5)
    r3.procesar_reserva()

    # 7. Falla por ValueError: Horas negativas o cero
    r4 = Reserva(c3, asesoria_ti, 0)
    r4.procesar_reserva()

    # 8. Falla encadenada: Exceso de horas
    r5 = Reserva(c1, asesoria_ti, 48)
    r5.procesar_reserva()

    # 9. Cálculo de costos con sobrecarga (Polimorfismo)
    print("9. Simulando cálculo de costos con diferentes parámetros (Sobrecarga):")
    print(f" Costo Sala con descuento: ${sala_juntas.calcular_costo(descuento=20000):.2f}")
    print(f" Costo Equipo sin seguro ni IVA: ${proyector.calcular_costo(impuestos=False, seguro_danos=0):.2f}")

    # 10. Listado de descripciones (Polimorfismo)
    print("\n10. Catálogo de Servicios (Demostración de Polimorfismo):")
    servicios = [sala_juntas, proyector, asesoria_ti]
    for s in servicios:
        print(f" - {s.describir()}")

if __name__ == "__main__":
    ejecutar_simulaciones()