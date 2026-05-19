# Sistema Integral de Gestión - Software FJ 

Proyecto final desarrollado para la *Fase 4 - Componente Práctico* del curso de Programación. Este aplicativo es un sistema de gestión de clientes, servicios y reservas que opera en memoria RAM sin uso de motores de bases de datos, priorizando la robustez y el manejo avanzado de excepciones.

# Características Principales

* **Programación Orientada a Objetos (POO):** Uso de clases abstractas, herencia, encapsulamiento y polimorfismo.
* **Gestión en Memoria:** Implementación de listas internas para simular bases de datos relacionales en tiempo de ejecución.
* **Manejo Avanzado de Excepciones:** Creación de excepciones personalizadas (`ValidacionClienteError`, `ServicioNoDisponibleError`, etc.), bloques `try/except/else/finally` y encadenamiento de errores para garantizar que el programa nunca se detenga de forma abrupta.
* **Sistema de Logging Automático:** Registro estructurado de eventos exitosos y trazabilidad de errores en el archivo físico `Errores.log`.
* **Interfaz Gráfica Moderna (GUI):** Interfaz desarrollada con `ttkbootstrap` (tema Superhero) que permite una navegación intuitiva por pestañas para registrar clientes, revisar el catálogo y asignar reservas.

# Requisitos Previos

Asegurarse de tener instalado Python 3.x en el sistema.
Para ejecutar la interfaz gráfica, es necesario instalar la librería `ttkbootstrap`:

```bash
pip install ttkbootstrap