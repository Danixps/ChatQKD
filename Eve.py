#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
# Diccionario que asocia el nombre del protocolo a la ruta del script a ejecutar

ruta_bb84 = os.path.join(base_dir, "BB84", "BB84-AEB", "eve.py")
ruta_bbm92 =  os.path.join(base_dir, "BBM92", "BBM92-AEB", "eve.py")
print(ruta_bb84)
protocol_files = {
    "BB84": ruta_bb84,
    "BBM92": ruta_bbm92,
    "E91": "/ruta/a/otro_archivo.py",  # Reemplaza esta ruta con la del otro protocolo
    "SARG04": "/ruta/a/otro_archivo.py"  # Reemplaza esta ruta con la del otro protocolo
}





def ejecutar_protocolo():
    protocolo = combo.get()
    if protocolo not in protocol_files:
        messagebox.showerror("Error", "Protocolo no válido.")
        return

    archivo = protocol_files[protocolo]
    
    # Verificar que el archivo exista
    if not os.path.exists(archivo):
        messagebox.showerror("Error", f"El archivo {archivo} no se encontró.")
        return

    # Ejemplo de una variable que queremos pasar al script (valor numérico)
    argumento = 100

    try:

        proc = subprocess.Popen(["python3", archivo, str(argumento)])
        
        # Esperamos a que el proceso termine (esto es bloqueante)
        proc.wait()
        
        # Si se completa correctamente se muestra un mensaje de éxito
        messagebox.showinfo("Éxito", f"El protocolo {protocolo} se ejecutó correctamente.")
        sys.exit(0)
        # En caso de que por algún motivo el proceso aun esté corriendo, se finaliza:
        if proc.poll() is None:
            proc.terminate()
            proc.wait()
            
    except subprocess.CalledProcessError as error:
        messagebox.showerror("Error", f"Error al ejecutar el protocolo {protocolo}.\nDetalles: {error}")
    except Exception as err:
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{err}")

# Configuración de la ventana principal
root = tk.Tk()
root.title("Selector de Protocolo")

# Creación y ubicación de los componentes (widgets)
frame = ttk.Frame(root, padding=100)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Etiqueta para la selección del protocolo
label = ttk.Label(frame, text="Seleccione un protocolo:")
label.grid(row=0, column=0, pady=5)

# Combobox para seleccionar el protocolo
combo = ttk.Combobox(frame, values=list(protocol_files.keys()), state="readonly")
combo.set("BB84")  # Valor por defecto
combo.grid(row=1, column=0, pady=5)

# Botón para ejecutar el protocolo seleccionado
button = ttk.Button(frame, text="Ejecutar", command=ejecutar_protocolo)
button.grid(row=2, column=0, pady=10)

# Inicia el bucle principal de la GUI
root.mainloop()