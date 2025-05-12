#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import time
import subprocess
import os
import sys
# Diccionario que asocia el nombre del protocolo a la ruta del script a ejecutar

base_dir = os.path.dirname(os.path.abspath(__file__))
# Diccionario que asocia el nombre del protocolo a la ruta del script a ejecutar

ruta_bb84 = os.path.join(base_dir, "BB84",  "reciever.py")
ruta_bbm92 =  os.path.join(base_dir, "BBM92",  "reciever.py")
ruta_E91 =  os.path.join(base_dir, "E91",  "reciever.py")
ruta_SARG04 = os.path.join(base_dir, "SARG04",  "reciever.py")

protocol_files = {
    "BB84": ruta_bb84,
    "BBM92": ruta_bbm92,  # Reemplaza esta ruta con la del otro protocolo
    "E91": ruta_E91,
    "SARG04": ruta_SARG04
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


    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 59006))
    s.listen(1)
    conn, addr = s.accept()

    # Recibir el nombre del protocolo del cliente (Alice)
    protocolo_recibido = conn.recv(1024).decode().strip()
    conn.sendall(protocolo.encode())
    if protocolo_recibido[-1] == 'E':
        #quitar ultima letra 
        protocolo_recibido = protocolo_recibido[:-1]
        time.sleep(20)
    if protocolo_recibido != protocolo:
        print(f"[ERROR] Protocolo incompatible: se esperaba {protocolo} pero se recibió {protocolo_recibido}")
        conn.sendall(b"ERROR: Protocolo no coincide.")
        conn.close()
        s.close()
        exit(1)
    s.close()
    print(f"Conectado con éxito a {addr[0]}:{addr[1]}")
    ###############
    
    time.sleep(3)
    try:

        proc = subprocess.Popen(["python3", archivo])
        
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
root.title("ChatQKD - Cliente")  # Cambiado a "ChatQKD"

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

label_author = ttk.Label(frame, text="Creado por Daniel Bensa Expósito Paz", foreground="gray")
label_author.grid(row=7, column=0, pady=(10, 5), sticky=tk.W)
# Inicia el bucle principal de la GUI
root.mainloop()