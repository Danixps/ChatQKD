#!/usr/bin/env python3
"""
@file Alice.py
@brief Interfaz gráfica para seleccionar y ejecutar protocolos de distribución cuántica de claves (QKD).
@author Daniel Bensa Exposito Paz
@date 2025-05-03
@version 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import time
import sys
import socket
base_dir = os.path.dirname(os.path.abspath(__file__))

# Rutas relativas a los protocolos
protocol_files = {
    "BB84": os.path.join(base_dir, "BB84", "sender.py"),
    "BBM92": os.path.join(base_dir, "BBM92", "sender.py"),
    "E91": os.path.join(base_dir, "E91", "sender.py"),
    "SARG04": os.path.join(base_dir, "SARG04", "sender.py")
}

# Niveles de seguridad predefinidos
security_levels = {
    "Bajo": 100,
    "Medio": 200,
    "Alto": 400
}

def actualizar_qubits(*args):
    """Actualiza el campo de entrada de qubits según el nivel de seguridad seleccionado."""
    nivel = combo_qubits.get()
    if nivel in security_levels:
        entry_num.delete(0, tk.END)
        entry_num.insert(0, str(security_levels[nivel]))

def ejecutar_protocolo():
    """Ejecuta el protocolo seleccionado con los parámetros introducidos por el usuario."""
    protocolo = combo.get()
    if protocolo not in protocol_files:
        messagebox.showerror("Error", "Protocolo no válido.")
        return

    archivo = protocol_files[protocolo]

    # Verificar existencia del archivo
    if not os.path.exists(archivo):
        messagebox.showerror("Error", f"El archivo {archivo} no se encontró.")
        return

    # Obtener número de qubits
    valor_str = entry_num.get()
    try:
        argumento = int(valor_str)
        if argumento <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingresa un número entero válido mayor que 0.")
        return

    # Obtener IP del servidor (opcional)
    ip = ip_entry.get().strip() or "localhost"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    max_reintentos = 5
    reintento = 0
    conectado = False
    # si se conecaa a 59001 no conecta a 59000
    if s.connect_ex((ip, 59009)) == 0:
        print(f"Conectado a {ip}:59000")
        conectado = True
    else:
        while reintento < max_reintentos:
            try:

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, 59006))
                conectado = True
                break
            except socket.error as e:
                print(f"[ERROR] No se pudo conectar a {ip}:59001. Reintentando... ({reintento + 1}/{max_reintentos})")
                time.sleep(2)
                reintento += 1
        # Si no se pudo conectar después de varios intentos, abortar
    

    if not conectado:
        print("No se pudo establecer conexión con Bob. Abortando.")
        exit(1)
    # Enviar el nombre del protocolo
    print(f"Conectado con éxito a {ip}:{59000}")
    s.sendall(protocolo.encode())

    # Recibir el nombre del protocolo del cliente (Bob)
    protocolo_recibido = s.recv(1024).decode().strip()
    s.close()
    if protocolo_recibido != protocolo:
        print(f"[ERROR] Protocolo incompatible: se esperaba {protocolo} pero se recibió {protocolo_recibido}")
        s.close()
        exit(1)
    try:
        proc = subprocess.Popen(["python3", archivo, str(argumento), ip])
        proc.wait()
        messagebox.showinfo("Éxito", f"El protocolo {protocolo} se ejecutó correctamente.")

        if proc.poll() is None:
            proc.terminate()
            proc.wait()

        sys.exit(0)

    except subprocess.CalledProcessError as error:
        messagebox.showerror("Error", f"Error al ejecutar el protocolo {protocolo}.\nDetalles: {error}")
    except Exception as err:
        messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{err}")

# ---------------- INTERFAZ ----------------
root = tk.Tk()
root.title("ChatQKD - Servidor")

frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Protocolo
ttk.Label(frame, text="Seleccione un protocolo:").grid(row=0, column=0, pady=5, sticky=tk.W)
combo = ttk.Combobox(frame, values=list(protocol_files.keys()), state="readonly")
combo.set("SARG04")
combo.grid(row=1, column=0, pady=5, sticky=tk.W)

# Nivel de seguridad
ttk.Label(frame, text="Seleccione el nivel de seguridad:").grid(row=2, column=0, pady=(15, 5), sticky=tk.W)
combo_qubits = ttk.Combobox(frame, values=list(security_levels.keys()), state="readonly")
combo_qubits.set("Medio")
combo_qubits.grid(row=3, column=0, pady=5, sticky=tk.W)
combo_qubits.bind("<<ComboboxSelected>>", actualizar_qubits)

# Número de qubits editable
ttk.Label(frame, text="Cantidad de qubits a enviar (puede editarse):").grid(row=4, column=0, pady=(15, 5), sticky=tk.W)
entry_num = ttk.Entry(frame, width=20)
entry_num.insert(0, str(security_levels["Medio"]))  # Inicializa con "Medio"
entry_num.grid(row=5, column=0, pady=5, sticky=tk.W)

# IP del servidor
ttk.Label(frame, text="IP del servidor (deja en blanco para localhost):").grid(row=6, column=0, pady=(15, 5), sticky=tk.W)
ip_entry = ttk.Entry(frame, width=20)
ip_entry.insert(0, "")
ip_entry.grid(row=7, column=0, pady=5, sticky=tk.W)

# Botón ejecutar
ttk.Button(frame, text="Ejecutar", command=ejecutar_protocolo).grid(row=8, column=0, pady=15, sticky=tk.W)

# Autoría
ttk.Label(frame, text="Creado por Daniel Bensa Expósito Paz", foreground="gray").grid(row=9, column=0, pady=(10, 5), sticky=tk.W)

# Llamar a actualización inicial
actualizar_qubits()

# Inicia la GUI
root.mainloop()
