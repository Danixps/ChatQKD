#!/usr/bin/env python3
"""
@file Alice.py
@brief Interfaz gráfica para seleccionar y ejecutar protocolos de distribución cuántica de claves (QKD).
@author Daniel Bensa Exposito Paz
@date 2025-05-03
@version 1.0
@details Esta aplicación permite al usuario seleccionar entre varios protocolos de QKD (BB84, BBM92, E91 y SARG04) y ejecutar el protocolo seleccionado con un número específico de qubits a enviar. La interfaz gráfica está construida utilizando Tkinter.
Este script es parte de un proyecto más grande que incluye varios protocolos de QKD, cada uno implementado en su propio archivo Python.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))

# Construcción de rutas relativas
ruta_bb84 = os.path.join(base_dir, "BB84", "sender.py")
ruta_bbm92 = os.path.join(base_dir, "BBM92", "sender.py")
ruta_E91 = os.path.join(base_dir, "E91", "sender.py")

# Definición de un diccionario que mapea los nombres de los protocolos a sus rutas de archivos correspondientes
protocol_files = {
    "BB84": ruta_bb84,
    "BBM92": ruta_bbm92,
    "E91": ruta_E91,     
    "SARG04": os.path.join(base_dir, "SARG04", "otro_script.py")     # Actualizar ruta según corresponda
}

def ejecutar_protocolo():
    """
    @brief Función para ejecutar el protocolo seleccionado.
    @details Esta función se activa al presionar el botón "Ejecutar". Verifica que el protocolo seleccionado y el número de qubits sean válidos, y luego ejecuta el protocolo correspondiente.
    @param None
    @return None
    """
    protocolo = combo.get()
    if protocolo not in protocol_files:
        messagebox.showerror("Error", "Protocolo no válido.")
        return

    archivo = protocol_files[protocolo]

    # Verificar que el archivo exista
    if not os.path.exists(archivo):
        messagebox.showerror("Error", f"El archivo {archivo} no se encontró.")
        return

    # Obtenemos el valor numérico introducido por el usuario
    valor_str = entry_num.get()
    try:
        argumento = int(valor_str)
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingresa un número entero válido.")
        return

    try:
        # Ejecutamos el proceso con Popen (para tener control sobre la finalización)
        proc = subprocess.Popen(["python3", archivo, str(argumento)])
        proc.wait()  # Espera a que el proceso termine

        # Se muestra mensaje de éxito
        messagebox.showinfo("Éxito", f"El protocolo {protocolo} se ejecutó correctamente.")

        # En caso de que aún el proceso siga en ejecución, se termina
        if proc.poll() is None:
            proc.terminate()
            proc.wait()

        # Finalizamos la ejecución del script actual
        sys.exit(0)
        
    except subprocess.CalledProcessError as error:
        messagebox.showerror("Error", f"Error al ejecutar el protocolo {protocolo}.\nDetalles: {error}")
    except Exception as err:
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{err}")

# Configuración de la ventana principal
root = tk.Tk()
root.title("Selector de Protocolo")

# Creación y ubicación de los componentes (widgets)
frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Etiqueta para la selección del protocolo
label_proto = ttk.Label(frame, text="Seleccione un protocolo:")
label_proto.grid(row=0, column=0, pady=5, sticky=tk.W)

# Combobox para seleccionar el protocolo
combo = ttk.Combobox(frame, values=list(protocol_files.keys()), state="readonly")
combo.set("BB84")  # Valor por defecto
combo.grid(row=1, column=0, pady=5, sticky=tk.W)

# Etiqueta y campo para introducir el número
label_num = ttk.Label(frame, text="Ingrese el número de qubits a enviar:")
label_num.grid(row=2, column=0, pady=(15, 5), sticky=tk.W)

entry_num = ttk.Entry(frame, width=20)
entry_num.insert(0, "100")  # Valor por defecto
entry_num.grid(row=3, column=0, pady=5, sticky=tk.W)

# Botón para ejecutar el protocolo seleccionado
button = ttk.Button(frame, text="Ejecutar", command=ejecutar_protocolo)
button.grid(row=4, column=0, pady=15, sticky=tk.W)

# Inicia el bucle principal de la GUI
root.mainloop()
