# Fase 4 - Componente Práctico
# Backend del Sistema Integral de Gestión - Software FJ

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
    """Clase base para excepciones del sistema Software FJ"""
    pass

class ValidacionClienteError(SoftwareFJError):
    pass

class ClienteDuplicadoError(SoftwareFJError):
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    pass

class ReservaInvalidaError(SoftwareFJError):
    pass

# ==================================================
# ISSUE #2: CLASES BASE, HERENCIA Y ENCAPSULAMIENTO
# ==================================================
class EntidadGeneral(ABC):
    """Clase abstracta para entidades generales del sistema"""
    @abstractmethod
    def mostrar_detalles(self):
        pass

class Cliente(EntidadGeneral):
    """Clase Cliente con encapsulación de datos personales"""
    def __init__(self, nombre, documento, correo):
        self.__nombre = nombre
        self.__documento = documento
        self.correo = correo  # Activa la validación del descriptor property

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

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
    """Clase abstracta Servicio"""
    def __init__(self, id_servicio, nombre, costo_base):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = True

    @abstractmethod
    def calcular_costo(self, impuestos=True, descuento=0):
        """Simulación de sobrecarga mediante parámetros opcionales"""
        pass

    @abstractmethod
    def describir(self):
        pass

class ReservaSalas(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, capacidad):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacity = capacidad

    def calcular_costo(self, impuestos=True, descuento=0):
        costo = self.costo_base - descuento
        if impuestos:
            costo *= 1.19  # IVA del 19%
        return costo

    def describir(self):
        return f"Sala '{self.nombre}' para {self.capacidad} personas."

class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, tipo_equipo):
        super().__init__(id_servicio, nombre, costo_base)
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, impuestos=True, descuento=0, seguro_danos=50000):
        costo = self.costo_base - descuento + seguro_danos
        return costo * 1.19 if impuestos else costo

    def describir(self):
        return f"Equipo: {self.nombre} ({self.tipo_equipo})."

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, consultor):
        super().__init__(id_servicio, nombre, costo_base)
        self.consultor = consultor

    def calcular_costo(self, impuestos=True, descuento=0):
        return self.costo_base - descuento

    def describir(self):
        return f"Asesoría en {self.nombre} por {self.consultor}."

# ==================================================
# LOGICA DE RESERVAS
# ==================================================
class Reserva:
    """Clase que integra Cliente, Servicio, Duración y Estado"""
    def __init__(self, cliente, servicio, horas):
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "Pendiente"

    def procesar_reserva(self):
        """Procesa la transacción aplicando try/except/else/finally y encadenamiento"""
        try:
            logging.info(f"Iniciando proceso de reserva para {self.cliente.mostrar_detalles()}")
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' ya está ocupado.")
            if self.horas <= 0:
                raise ValueError("La cantidad de horas debe ser mayor a cero.")
            
            if self.horas > 24:
                 try:
                     raise OverflowError("Exceso de horas permitidas en una simulación diaria")
                 except OverflowError as e:
                     raise ReservaInvalidaError("Reserva excede el límite operativo diario") from e
            
            self.servicio.disponible = False
            self.estado = "Confirmada"
            costo_total = self.servicio.calcular_costo() * self.horas
            logging.info(f"Reserva exitosa: {self.servicio.nombre}. Total: ${costo_total:.2f}")
            return costo_total

        except ServicioNoDisponibleError as e:
            logging.error(f"Fallo de disponibilidad: {e}")
            self.estado = "Fallida"
            raise
        except ValidacionClienteError as e:
            logging.error(f"Error de validación del cliente: {e}")
            self.estado = "Fallida"
            raise
        except ReservaInvalidaError as e:
            logging.error(f"Reserva inválida: {e}. Causa original: {e.__cause__}")
            self.estado = "Fallida"
            raise
        except Exception as e:
            logging.error(f"Error inesperado procesando la reserva: {e}")
            self.estado = "Fallida"
            raise
        else:
            logging.info("Cláusula ELSE: Bloque try ejecutado exitosamente sin excepciones.")
        finally:
            logging.info(f"Cláusula FINALLY: Finalizando transacción de reserva. Estado final: {self.estado}")


# =================================================================
# ISSUE #5: ENTORNO CENTRALIZADO - GESTIÓN MEDIANTE LISTAS INTERNAS
# =================================================================
class EmpresaSoftwareFJ:
    """Controlador central que actúa como base de datos relacional en memoria RAM"""
    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []

    # --- Métodos de registro con validaciones estrictas ---
    def registrar_cliente(self, cliente):
        for c in self.__clientes:
            if c.documento == cliente.documento:
                raise ClienteDuplicadoError(f"El documento {cliente.documento} ya se encuentra registrado.")
        self.__clientes.append(cliente)
        logging.info(f"Cliente registrado en lista interna de forma exitosa: {cliente.documento}")

    def agregar_servicio(self, servicio):
        self.__servicios.append(servicio)
        logging.info(f"Servicio añadido al catálogo interno de forma exitosa: {servicio.id_servicio}")

    def crear_reserva(self, cliente, servicio, horas):
        reserva = Reserva(cliente, servicio, horas)
        self.__reservas.append(reserva)
        costo = reserva.procesar_reserva()
        return reserva, costo

    # --- Métodos de lectura (Getters para alimentar la futura GUI del Issue 6) ---
    def obtener_clientes(self):
        return self.__clientes

    def obtener_servicios(self):
        return self.__servicios

    def obtener_reservas(self):
        return self.__reservas


# =================================================================
# ISSUE #4: ENTORNO DE PRUEBAS AUTOMATIZADAS (10 SIMULACIONES)
# =================================================================
def ejecutar_simulaciones():
    print("================================================================")
    print("   EJECUTANDO PANEL DE SIMULACIONES CONTROLADAS - SOFTWARE FJ   ")
    print("================================================================\n")
    
    # Instanciamos nuestra base de datos relacional en memoria
    core_app = EmpresaSoftwareFJ()

    # 1. Registro exitoso de cliente
    print("[Operación 1/10] Intentando registro de cliente válido...")
    try:
        dan = Cliente("Daniel Vanegas", "101010", "davanegas@unad.edu.co")
        core_app.registrar_cliente(dan)
        print(f" -> Éxito: {dan.mostrar_detalles()} guardado en la lista interna.")
    except Exception as e:
        print(f" -> Fallo inesperado: {e}")
    print("-" * 65)

    # 2. Registro fallido de cliente (Correo erróneo capturado por ValidaciónClienteError)
    print("[Operación 2/10] Intentando registro de cliente con correo inválido...")
    try:
        manu = Cliente("Manuela Rosas", "202020", "manuela-sin-arroba-y-punto")
        core_app.registrar_cliente(manu)
    except ValidacionClienteError as e:
        print(f" -> CONTROLADO (Excepción): {e}")
    print("-" * 65)

    # 3. Registro fallido por duplicidad de datos (Requisito estricto de listas del Issue #5)
    print("[Operación 3/10] Intentando registrar cliente con documento duplicado...")
    try:
        clon_dan = Cliente("Daniel Clon", "101010", "clon.dan@unad.edu.co")
        core_app.registrar_cliente(clon_dan)
    except ClienteDuplicadoError as e:
        print(f" -> CONTROLADO (Excepción de Negocio): {e}")
    print("-" * 65)

    # 4. Creación correcta de servicios en el catálogo
    print("[Operación 4/10] Inicializando catálogo de servicios en la lista interna...")
    sala_vip = ReservaSalas("S01", "Sala de Juntas VIP", 100000, 15)
    proyector = AlquilerEquipos("E01", "Proyector Láser 4K", 50000, "Audiovisual")
    asesoria_ti = AsesoriaEspecializada("A01", "Auditoría de Ciberseguridad", 200000, "Ing. Juan Manuel")
    
    core_app.agregar_servicio(sala_vip)
    core_app.agregar_servicio(proyector)
    core_app.agregar_servicio(asesoria_ti)
    print(f" -> Éxito: {len(core_app.obtener_servicios())} servicios cargados dinámicamente en memoria.")
    print("-" * 65)

    # 5. Reserva exitosa utilizando objetos mapeados de listas
    print("[Operación 5/10] Procesando solicitud de reserva válida (Sala VIP)...")
    try:
        reserva, total = core_app.crear_reserva(dan, sala_vip, 3)
        print(f" -> ÉXITO: Reserva {reserva.estado}. Total a facturar: ${total:.2f}")
    except Exception as e:
        print(f" -> Error en procesamiento: {e}")
    print("-" * 65)

    # 6. Reserva fallida: Servicio no disponible (Garantiza consistencia del modelo de negocio)
    print("[Operación 6/10] Forzando conflicto de asignación sobre el mismo servicio...")
    try:
        luna = Cliente("Luna Galindo", "303030", "luna@unad.edu.co")
        core_app.registrar_cliente(luna)
        # Se intenta reservar la sala VIP que ya fue ocupada en la operación 5
        reserva, total = core_app.crear_reserva(luna, sala_vip, 2)
    except ServicioNoDisponibleError as e:
        print(f" -> CONTROLADO (Excepción de Disponibilidad): {e}")
    print("-" * 65)

    # 7. Reserva exitosa con sobrecarga de costos implícita
    print("[Operación 7/10] Procesando reserva de equipo (Aplica tarifas dinámicas de seguro)...")
    try:
        reserva, total = core_app.crear_reserva(dan, proyector, 5)
        print(f" -> ÉXITO: Reserva {reserva.estado}. Facturado con seguro de daños e IVA: ${total:.2f}")
    except Exception as e:
        print(f" -> Error en procesamiento: {e}")
    print("-" * 65)

    # 8. Reserva fallida por paso de parámetros erróneos (ValueError)
    print("[Operación 8/10] Ejecutando control de rangos operativos (Horas cero)...")
    try:
        reserva, total = core_app.crear_reserva(luna, asesoria_ti, 0)
    except ValueError as e:
        print(f" -> CONTROLADO (Excepción de Argumento): {e}")
    print("-" * 65)

    # 9. Reserva fallida con encadenamiento explícito de excepciones (Raise ... from)
    print("[Operación 9/10] Provocando desbordamiento de límites de tiempo (Encadenamiento)...")
    try:
        reserva, total = core_app.crear_reserva(dan, asesoria_ti, 48)
    except ReservaInvalidaError as e:
        print(f" -> CONTROLADO (Excepción Encadenada): {e}")
        print(f"    Causa Raíz subyacente del sistema: {type(e.__cause__).__name__} -> {e.__cause__}")
    print("-" * 65)

    # 10. Demostración de Polimorfismo puro inspeccionando las colecciones de objetos
    print("[Operación 10/10] Extrayendo catálogo estructurado (Enfoque polimórfico)...")
    print("      Catálogo vigente en la lista de servicios:")
    for item in core_app.obtener_servicios():
        print(f"      * [{item.id_servicio}] {item.describir()}")
    print("\n================================================================")
    print("   SIMULACIONES COMPLETADAS: EL SISTEMA CONTINÚA ESTABLE (OK)   ")
    print("================================================================")

if __name__ == "__main__":
    ejecutar_simulaciones()