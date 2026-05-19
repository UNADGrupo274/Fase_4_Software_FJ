# Fase 4 - Componente Práctico - Prácticas Simuladas
# Sistema Integral de Gestión - Software FJ

# Importamos las librerías necesarias para el registro de errores, la creación de la interfaz y la abstracción de clases
import logging
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from abc import ABC, abstractmethod

# ======================
# CONFIGURACIÓN DE LOGS
# ======================
# Configuramos el sistema de registro (logs) para guardar los eventos y errores en un archivo de texto plano
logging.basicConfig(
    filename='Errores.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ===========================
# EXCEPCIONES PERSONALIZADAS
# ===========================
# Definimos nuestras propias excepciones heredando de la clase base Exception para un manejo de errores más específico
class SoftwareFJError(Exception): pass
class ValidacionClienteError(SoftwareFJError): pass
class ClienteDuplicadoError(SoftwareFJError): pass
class ServicioNoDisponibleError(SoftwareFJError): pass
class ReservaInvalidaError(SoftwareFJError): pass

# ========================================
# CLASES BASE, HERENCIA Y ENCAPSULAMIENTO
# ========================================
# Creamos la clase abstracta base de la cual heredarán otras entidades
class EntidadGeneral(ABC):
    @abstractmethod
    def mostrar_detalles(self): pass

# Implementamos la clase Cliente con encapsulamiento estricto en sus atributos principales
class Cliente(EntidadGeneral):
    def __init__(self, nombre, documento, correo):
        self.__nombre = nombre
        self.__documento = documento
        self.correo = correo  

    # Utilizamos decoradores property para permitir el acceso controlado a los atributos privados
    @property
    def nombre(self): return self.__nombre

    @property
    def documento(self): return self.__documento

    @property
    def correo(self): return self.__correo

    # Validamos el formato del correo electrónico antes de asignarlo, lanzando un error si es incorrecto
    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise ValidacionClienteError(f"Formato de correo inválido: {valor}")
        self.__correo = valor

    # Sobrescribimos el método abstracto para mostrar los datos del cliente
    def mostrar_detalles(self):
        return f"Cliente: {self.__nombre} (Doc: {self.__documento})"

# Definimos la clase abstracta Servicio que servirá como plantilla para los diferentes tipos de servicios
class Servicio(ABC):
    def __init__(self, id_servicio, nombre, costo_base):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = True # Establecemos la disponibilidad por defecto en True

    # Declaramos los métodos abstractos que las clases hijas deberán implementar obligatoriamente
    @abstractmethod
    def calcular_costo(self, impuestos=True, descuento=0): pass

    @abstractmethod
    def describir(self): pass

# Heredamos de Servicio para crear el servicio específico de Reserva de Salas
class ReservaSalas(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, capacidad):
        super().__init__(id_servicio, nombre, costo_base)
        self.capacidad = capacidad

    # Calculamos el costo aplicando polimorfismo, incluyendo la lógica de impuestos para las salas
    def calcular_costo(self, impuestos=True, descuento=0):
        costo = self.costo_base - descuento
        return costo * 1.19 if impuestos else costo

    def describir(self):
        return f"Sala '{self.nombre}' ({self.capacidad} pers.)"

# Heredamos de Servicio para el Alquiler de Equipos, agregando el parámetro de seguro por daños
class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, tipo_equipo):
        super().__init__(id_servicio, nombre, costo_base)
        self.tipo_equipo = tipo_equipo

    # Calculamos el costo sobrecargando la lógica para incluir el seguro obligatorio
    def calcular_costo(self, impuestos=True, descuento=0, seguro_danos=50000):
        costo = self.costo_base - descuento + seguro_danos
        return costo * 1.19 if impuestos else costo

    def describir(self):
        return f"Equipo: {self.nombre} ({self.tipo_equipo})"

# Heredamos de Servicio para Asesorías Especializadas
class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, costo_base, consultor):
        super().__init__(id_servicio, nombre, costo_base)
        self.consultor = consultor

    # Calculamos el costo de la asesoría (en este caso, exento de impuestos por regla de negocio)
    def calcular_costo(self, impuestos=True, descuento=0):
        return self.costo_base - descuento

    def describir(self):
        return f"Asesoría: {self.nombre} por {self.consultor}"

# ===================
# LÓGICA DE RESERVAS
# ===================
# Creamos la clase Reserva que integra a los clientes con los servicios
class Reserva:
    def __init__(self, cliente, servicio, horas):
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "Pendiente" # Asignamos el estado inicial de la reserva

    # Procesamos la reserva aplicando un bloque robusto de try-except-finally
    def procesar_reserva(self):
        try:
            # Registramos el inicio del proceso en el archivo log
            logging.info(f"Procesando reserva para {self.cliente.mostrar_detalles()}")
            
            # Verificamos si el servicio está disponible
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' está ocupado.")
            
            # Comprobamos que las horas solicitadas sean lógicas y válidas
            if self.horas <= 0:
                raise ValueError("Las horas deben ser mayores a cero.")
            
            # Evaluamos si excede el límite permitido, encadenando excepciones si es el caso
            if self.horas > 24:
                 try:
                     raise OverflowError("Exceso de horas")
                 except OverflowError as e:
                     raise ReservaInvalidaError("Reserva excede el límite de 24h") from e
            
            # Actualizamos el estado del servicio y de la reserva al superar las validaciones
            self.servicio.disponible = False
            self.estado = "Confirmada"
            costo_total = self.servicio.calcular_costo() * self.horas
            logging.info(f"Reserva exitosa. Total: ${costo_total:.2f}")
            return costo_total

        except Exception as e:
            # Capturamos cualquier error, cambiamos el estado y registramos la falla
            self.estado = "Fallida"
            logging.error(f"Error procesando reserva: {e}")
            raise 
        finally:
            # Garantizamos que siempre se registre el fin de la transacción, haya error o no
            logging.info(f"Transacción finalizada. Estado: {self.estado}")

# =======================================
# GESTIÓN CENTRALIZADA (LISTAS INTERNAS)
# =======================================
# Centralizamos la gestión de datos simulando una base de datos en memoria RAM
class EmpresaSoftwareFJ:
    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        self._precargar_servicios() # Precargamos servicios para tener datos iniciales en la interfaz

    # Agregamos servicios predeterminados al sistema
    def _precargar_servicios(self):
        self.agregar_servicio(ReservaSalas("S01", "Sala de Juntas VIP", 100000, 15))
        self.agregar_servicio(AlquilerEquipos("E01", "Proyector Láser 4K", 50000, "Audiovisual"))
        self.agregar_servicio(AsesoriaEspecializada("A01", "Auditoría TI", 200000, "Ing. Juan Manuel"))

    # Registramos un nuevo cliente validando que su documento no exista previamente
    def registrar_cliente(self, cliente):
        for c in self.__clientes:
            if c.documento == cliente.documento:
                raise ClienteDuplicadoError(f"El documento {cliente.documento} ya existe.")
        self.__clientes.append(cliente)
        logging.info(f"Cliente registrado: {cliente.documento}")

    # Añadimos un servicio a la lista interna
    def agregar_servicio(self, servicio):
        self.__servicios.append(servicio)

    # Creamos y procesamos una reserva integrando cliente y servicio
    def crear_reserva(self, cliente, servicio, horas):
        reserva = Reserva(cliente, servicio, horas)
        costo = reserva.procesar_reserva()
        self.__reservas.append(reserva)
        return reserva, costo

    # Proveemos métodos para obtener las listas encapsuladas
    def obtener_clientes(self): return self.__clientes
    def obtener_servicios(self): return self.__servicios
    def obtener_reservas(self): return self.__reservas

# ==================================
# INTERFAZ GRÁFICA CON TTKBOOTSTRAP
# ==================================
# Construimos la interfaz gráfica de usuario (GUI) heredando de la ventana de ttkbootstrap
class AppSoftwareFJ(tb.Window):
    def __init__(self, backend):
        super().__init__(themename="superhero") # Establecemos el tema visual de la ventana
        self.title("Software FJ - Gestión Integral")
        self.geometry("800x600")
        self.backend = backend

        # Colocamos el título principal de la aplicación
        titulo = tb.Label(self, text="Sistema de Gestión - Software FJ", font=("Helvetica", 18, "bold"))
        titulo.pack(pady=15)

        # Creamos el contenedor de pestañas (Notebook) para organizar las secciones
        self.notebook = tb.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Asignamos un marco (Frame) independiente para cada pestaña
        self.tab_clientes = tb.Frame(self.notebook)
        self.tab_servicios = tb.Frame(self.notebook)
        self.tab_reservas = tb.Frame(self.notebook)

        # Agregamos los marcos al Notebook con sus respectivos nombres
        self.notebook.add(self.tab_clientes, text="👥 Gestión de Clientes")
        self.notebook.add(self.tab_servicios, text="📦 Catálogo de Servicios")
        self.notebook.add(self.tab_reservas, text="📅 Panel de Reservas")

        # Construimos todos los componentes de cada pestaña secuencialmente
        self.construir_tab_clientes()
        self.construir_tab_servicios()
        self.construir_tab_reservas()
        
        # Una vez que todo existe en la interfaz, actualizamos las tablas con los datos en memoria
        self.actualizar_tablas()

    # --- PESTAÑA CLIENTES ---
    # Diseñamos la estructura visual para la gestión de clientes
    def construir_tab_clientes(self):
        marco_form = tb.LabelFrame(self.tab_clientes, text=" Registrar Nuevo Cliente ")
        marco_form.pack(fill=X, padx=20, pady=10)

        # Ubicamos los campos de texto (Entry) y sus etiquetas usando el gestor Grid
        tb.Label(marco_form, text="Nombre:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.ent_nombre = tb.Entry(marco_form, width=30)
        self.ent_nombre.grid(row=0, column=1, padx=10, pady=5)

        tb.Label(marco_form, text="Documento:").grid(row=0, column=2, padx=10, pady=5, sticky=W)
        self.ent_doc = tb.Entry(marco_form, width=20)
        self.ent_doc.grid(row=0, column=3, padx=10, pady=5)

        tb.Label(marco_form, text="Correo:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        self.ent_correo = tb.Entry(marco_form, width=30)
        self.ent_correo.grid(row=1, column=1, padx=10, pady=5)

        # Añadimos el botón que dispara la función para guardar el cliente
        btn_guardar = tb.Button(marco_form, text="Guardar Cliente", bootstyle="success", command=self.guardar_cliente)
        btn_guardar.grid(row=1, column=3, pady=10, sticky=E)

        # Configuramos la tabla (Treeview) para mostrar la lista de clientes registrados
        columnas = ("doc", "nombre", "correo")
        self.tree_clientes = tb.Treeview(self.tab_clientes, columns=columnas, show="headings", bootstyle="info")
        self.tree_clientes.heading("doc", text="Documento")
        self.tree_clientes.heading("nombre", text="Nombre")
        self.tree_clientes.heading("correo", text="Correo Electrónico")
        self.tree_clientes.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Extraemos y validamos los datos ingresados en el formulario de clientes
    def guardar_cliente(self):
        nombre = self.ent_nombre.get().strip()
        doc = self.ent_doc.get().strip()
        correo = self.ent_correo.get().strip()

        # Comprobamos que no se envíen campos vacíos
        if not nombre or not doc or not correo:
            Messagebox.show_warning("Todos los campos son obligatorios.", "Advertencia")
            return

        try:
            # Instanciamos al cliente y lo registramos en el backend
            nuevo_cliente = Cliente(nombre, doc, correo)
            self.backend.registrar_cliente(nuevo_cliente)
            
            # Actualizamos la vista y limpiamos los campos del formulario tras el éxito
            self.actualizar_tablas()
            self.ent_nombre.delete(0, END)
            self.ent_doc.delete(0, END)
            self.ent_correo.delete(0, END)
            Messagebox.show_info("Cliente registrado con éxito.", "Éxito")
        
        # Atrapamos y mostramos los errores de validación directamente al usuario mediante pop-ups
        except ValidacionClienteError as e:
            Messagebox.show_error(str(e), "Error de Validación")
        except ClienteDuplicadoError as e:
            Messagebox.show_error(str(e), "Error de Duplicidad")
        except Exception as e:
            Messagebox.show_error(f"Error inesperado: {e}", "Error")

   # --- PESTAÑA SERVICIOS ---
    # Construimos la visualización del catálogo de servicios disponibles
    def construir_tab_servicios(self):
        tb.Label(self.tab_servicios, text="Servicios Disponibles en Memoria:", font=("Helvetica", 12)).pack(pady=10, anchor=W, padx=20)
        
        # Preparamos la tabla (Treeview) para enlistar los servicios
        columnas = ("id", "desc", "costo", "estado")
        self.tree_servicios = tb.Treeview(self.tab_servicios, columns=columnas, show="headings", bootstyle="primary")
        self.tree_servicios.heading("id", text="ID")
        self.tree_servicios.column("id", width=50)
        self.tree_servicios.heading("desc", text="Descripción")
        self.tree_servicios.heading("costo", text="Costo Base")
        self.tree_servicios.heading("estado", text="Disponibilidad")
        self.tree_servicios.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # --- PESTAÑA RESERVAS ---
    # Elaboramos el formulario para asignar servicios a los clientes
    def construir_tab_reservas(self):
        marco_form = tb.LabelFrame(self.tab_reservas, text=" Generar Reserva ")
        marco_form.pack(fill=X, padx=20, pady=10)

        # Incorporamos menús desplegables (Combobox) para seleccionar clientes y servicios existentes
        tb.Label(marco_form, text="Cliente:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.cb_clientes = tb.Combobox(marco_form, width=35, state="readonly")
        self.cb_clientes.grid(row=0, column=1, padx=10, pady=5)

        tb.Label(marco_form, text="Servicio:").grid(row=1, column=0, padx=10, pady=5, sticky=W)
        self.cb_servicios = tb.Combobox(marco_form, width=35, state="readonly")
        self.cb_servicios.grid(row=1, column=1, padx=10, pady=5)

        tb.Label(marco_form, text="Horas:").grid(row=2, column=0, padx=10, pady=5, sticky=W)
        self.ent_horas = tb.Entry(marco_form, width=10)
        self.ent_horas.grid(row=2, column=1, padx=10, pady=5, sticky=W)

        # Colocamos el botón para ejecutar la lógica de reserva
        btn_reservar = tb.Button(marco_form, text="Confirmar Reserva", bootstyle="warning", command=self.procesar_reserva)
        btn_reservar.grid(row=2, column=1, pady=10, sticky=E)

        # Instanciamos la tabla que actuará como historial de reservas realizadas
        columnas = ("cliente", "servicio", "horas", "estado")
        self.tree_reservas = tb.Treeview(self.tab_reservas, columns=columnas, show="headings", bootstyle="warning")
        self.tree_reservas.heading("cliente", text="Cliente")
        self.tree_reservas.heading("servicio", text="Servicio")
        self.tree_reservas.heading("horas", text="Horas")
        self.tree_reservas.heading("estado", text="Estado")
        self.tree_reservas.pack(fill=BOTH, expand=True, padx=20, pady=10)

    # Gestionamos el evento de confirmar una reserva desde la interfaz
    def procesar_reserva(self):
        # Obtenemos los índices seleccionados en los combobox
        idx_cliente = self.cb_clientes.current()
        idx_servicio = self.cb_servicios.current()
        
        # Validamos que se haya seleccionado un cliente y un servicio
        if idx_cliente == -1 or idx_servicio == -1:
            Messagebox.show_warning("Seleccione un cliente y un servicio.", "Advertencia")
            return
            
        try:
            # Capturamos las horas y recuperamos los objetos completos desde el backend
            horas = int(self.ent_horas.get())
            cliente_obj = self.backend.obtener_clientes()[idx_cliente]
            servicio_obj = self.backend.obtener_servicios()[idx_servicio]

            # Ejecutamos la reserva e informamos al usuario sobre el éxito y el costo
            reserva, total = self.backend.crear_reserva(cliente_obj, servicio_obj, horas)
            Messagebox.show_info(f"Reserva confirmada.\nCosto Total: ${total:,.2f}", "Éxito")
            
            # Limpiamos el campo de horas y repintamos las tablas para reflejar la disponibilidad
            self.ent_horas.delete(0, END)
            self.actualizar_tablas()

        # Interceptamos todos los errores posibles y los mostramos gráficamente sin romper el sistema
        except ValueError:
            Messagebox.show_error("La cantidad de horas debe ser un número entero válido.", "Error de Formato")
        except ServicioNoDisponibleError as e:
            Messagebox.show_error(str(e), "Servicio Ocupado")
        except ReservaInvalidaError as e:
            Messagebox.show_error(str(e), "Límites Excedidos")
        except Exception as e:
            Messagebox.show_error(f"Ocurrió un error procesando la reserva:\n{e}", "Error del Sistema")

    # Sincronizamos los datos del backend con los elementos visuales de la interfaz
    def actualizar_tablas(self):
        # Limpiamos y repoblamos el Treeview y el Combobox de Clientes
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        lista_clientes = []
        for c in self.backend.obtener_clientes():
            self.tree_clientes.insert("", END, values=(c.documento, c.nombre, c.correo))
            lista_clientes.append(f"{c.documento} - {c.nombre}")
        self.cb_clientes['values'] = lista_clientes

        # Limpiamos y repoblamos el Treeview y el Combobox de Servicios verificando su estado
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        lista_servicios = []
        for s in self.backend.obtener_servicios():
            estado = "Disponible" if s.disponible else "Ocupado"
            self.tree_servicios.insert("", END, values=(s.id_servicio, s.describir(), f"${s.costo_base:,.2f}", estado))
            lista_servicios.append(f"{s.id_servicio} - {s.nombre}")
        self.cb_servicios['values'] = lista_servicios

        # Limpiamos y repoblamos el historial visual de Reservas
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        for r in self.backend.obtener_reservas():
            self.tree_reservas.insert("", END, values=(r.cliente.nombre, r.servicio.nombre, r.horas, r.estado))

# ====================================
# BLOQUE PRINCIPAL (PUNTO DE ENTRADA)
# ====================================
# Verificamos que el script se esté ejecutando directamente y no siendo importado
if __name__ == "__main__":
    # Las simulaciones para consola (Issue #4) están disponibles en versiones anteriores del commit 
    # y en el registro de la terminal para el informe.
    # Aquí se inicializa el entorno visual de producción final.
    
    # Instanciamos la clase central del sistema que maneja la memoria y la lógica
    app_backend = EmpresaSoftwareFJ()
    
    # Creamos la ventana principal pasándole nuestro backend
    interfaz = AppSoftwareFJ(app_backend)
    
    # Centramos la ventana en la pantalla del usuario
    interfaz.place_window_center()
    
    # Arrancamos el bucle principal de eventos para mantener la ventana en ejecución
    interfaz.mainloop()