"""
@file: sender.py
@brief: Este archivo contiene la implementación de un servidor que envía qubits a un cliente (Bob) y permite la comunicación segura entre Alice y Bob utilizando criptografía cuántica.
@author Daniel Bensa Exposito Paz
@details: El servidor utiliza sockets para la comunicación y AES para cifrar los mensajes. Se implementa un protocolo de intercambio de claves cuánticas (QKD) para generar una clave compartida segura entre Alice y Bob.
@date: 2025-05-03
@version: 1.0
@note: Este código es parte de un sistema de intercambio de claves cuánticas y utiliza la biblioteca Qiskit para simular circuitos cuánticos.
"""
import socket
import threading
import numpy as np
import pickle
import struct
import random
from qiskit import QuantumCircuit
from Crypto.Cipher import AES
from datetime import datetime
import hashlib
import tkinter as tk
import os
import time

SIZE = 10

import sys

if len(sys.argv) > 1:
    try:
        SIZE = int(sys.argv[1])
        print(f"El tamaño recibido es: {SIZE}")
    except ValueError:
        print("El argumento debe ser un entero.")
        sys.exit(1)
else:
    print("No se recibió ningún argumento.")
    sys.exit(1)
    
def bind_socket(server_socket, address, event, stop_event, conn_list):
    try:
        server_socket.bind(address)
        server_socket.listen(1)

        while not event.is_set():
            server_socket.settimeout(1)
            try:
                conn, addr = server_socket.accept()
                print(f"Conexión aceptada en {address}")
                conn_list.append(conn)
                event.set()
                break
            except socket.timeout:
                if stop_event.is_set():
                    #print(f"Terminando espera en {address}")
                    break
    except Exception as e:
        print(f"Error en {address}: {e}")
    finally:
        server_socket.close()

def decrypt_message(encrypted_message, aes_key, tag, nonce):
    cipher_dec = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext_dec = cipher_dec.decrypt_and_verify(encrypted_message, tag)
    return plaintext_dec.decode()

def derive_aes_key(shared_key):
    key = hashlib.sha256(shared_key).digest()[:16]
    return key

def encrypt_message(message, aes_key):
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    nonce = get_random_bytes(12)
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return [ciphertext, tag, nonce]

def start_sender():
    conn = None
    conn1 = None
    conn2 = None
    try:
        print(f"Esperando conexión...")
        connection_event = threading.Event()
        stop_event = threading.Event()
        conn_list = []

        server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        thread1 = threading.Thread(target=bind_socket, args=(server_socket1, ('localhost', 65431), connection_event, stop_event, conn_list))
        thread2 = threading.Thread(target=bind_socket, args=(server_socket2, ('localhost', 65458), connection_event, stop_event, conn_list))

        thread1.start()
        thread2.start()

        connection_event.wait()
        stop_event.set()

        thread1.join()
        thread2.join()

        conn = conn_list[0]
        

        alice_bits = np.random.randint(2, size=SIZE)
        alice_states = np.random.choice(['1', '0', '-', '+'], size=SIZE)
        print("\n-----------------FASE DE ENVÍO DE CÚBITS A BOB-----------------")
        print("Estados a enviar", alice_states)
        print("Bits de Alice: ", alice_bits)
        circuits = []
        pairs_to_key = []
        pairs = []


        for i in range(SIZE):
            state = alice_states[i]
            qc = QuantumCircuit(1, 1)

            # Preparar el estado
            if state == '0':
                pass  # |0⟩ es el estado por defecto
            elif state == '1':
                qc.x(0)  # X|0⟩ = |1⟩
            elif state == '+':
                qc.x(0)      # Primero |1⟩
                qc.h(0)  # H|0⟩ = |+⟩
            elif state == '-':
                qc.h(0)      # H|1⟩ = |−⟩

            circuits.append(qc)

            # Mostrar información
           
            if state == '-' or state == '+':
                random_state = random.choice(['0', '1'])
                pairs_to_key.append(random_state)
                pairs.append((random_state, state[0]))  
            else:
                random_state = random.choice(['+', '-'])
                pairs.append((state[0], random_state))
                pairs_to_key.append(random_state)

              
            
           
            # Opcional: obtener el estado vectorial de alguno

        
        serialized_circuits = pickle.dumps(circuits)
        data_length = struct.pack('!I', len(serialized_circuits))
        conn.sendall(data_length)
        conn.sendall(serialized_circuits)
        # Convertir la lista de tuplas en una cadena
        pairs_str = ''.join([str(pair) for pair in pairs])

        # Convertir la cadena resultante a bytes
        send_pairs = bytes(pairs_str, 'utf-8')

        # Imprimir el resultado
        print(send_pairs)
        data_length= struct.pack('!I', len(send_pairs))
        time.sleep(0.01)
        conn.sendall(data_length)
        conn.sendall(send_pairs)

        print ("Estados correspondientes:", alice_states)
        print("Qubits enviados exitosamente.")

        print ("Pares de estados a enviar:", pairs)



      

        server_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       
        server_socket3.bind(('localhost', 65489))
        server_socket3.listen(1)
        conn1, addr1 = server_socket3.accept()
        

        data = []
       
    
        while len(b"".join(data)) < SIZE:
            packet = conn1.recv(99999)
            if not packet:
                break
            data.append(packet)

        
        # Concatenar todos los bytes
        received_bytes = b"".join(data)
        
        # Deserializar índices como enteros (4 bytes por índice)
        indices = []
        for i in range(0, len(received_bytes), 4):  # Cada índice ocupa 4 bytes
            index_bytes = received_bytes[i:i+4]
            if len(index_bytes) == 4:  # Asegura que hay suficientes bytes
                index = struct.unpack('!i', index_bytes)[0]
                indices.append(index)
        lista_indice_enteros = indices


        server_socket9 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket9.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       
        server_socket9.bind(('localhost', 62222))
        server_socket9.listen(1)
        conn9, addr9 = server_socket9.accept()
        data = []
        while len(b"".join(data)) < (len(lista_indice_enteros) // 3):
            packet = conn9.recv(99999)
            if not packet:
                break
            data.append(packet)
        received_bytes = b"".join(data)
        
        # Deserializar índices como enteros (4 bytes por índice)
        indices_comprobacion = []
        for i in range(0, len(received_bytes), 4):  # Cada índice ocupa 4 bytes
            index_bytes = received_bytes[i:i+4]
            if len(index_bytes) == 4:  # Asegura que hay suficientes bytes
                index = struct.unpack('!i', index_bytes)[0]
                indices_comprobacion.append(index)
        indices_comprobacion_enteros = indices_comprobacion
        
        print(f"indices recibidos: {indices}")
        print(f"Indices de comprobación recibidos: {indices_comprobacion_enteros}")



        data = []
        while len(b"".join(data)) < (len(lista_indice_enteros) // 3):
            packet = conn9.recv(99999)
            if not packet:
                break
            data.append(packet)
        received_bytes = b"".join(data)

        # Deserializar índices como enteros (4 bytes por índice)
        bits_comprobacion = []
        for i in range(0, len(received_bytes), 4):  # Cada índice ocupa 4 bytes
            index_bytes = received_bytes[i:i+4]
            if len(index_bytes) == 4:  # Asegura que hay suficientes bytes
                bit = struct.unpack('!i', index_bytes)[0]
                bits_comprobacion.append(bit)
        bits_comprobacion_enteros = bits_comprobacion
        print(f"Bit de comprobación recibidos: {bits_comprobacion_enteros}")





        print("\n-----------------FASE DE COMPROBACIÓN-----------------")
        print("Indices de la clave compartida Bob:", lista_indice_enteros)
        
        shared_key = [pairs_to_key[i] for i in lista_indice_enteros]
        shared_key_str = [str(item) for item in shared_key]
        shared_key_bit = ['0' if x == '+' else '1' if x == '-' else x for x in shared_key_str]
        key = [int(bit) for bit in shared_key_bit]
        
       
        pairs_to_key_str = ['0' if x == '+' else '1' if x == '-' else x for x in pairs_to_key]
        pairs_to_key_int = [int(bit) for bit in pairs_to_key_str]

        bits_comrpobacion_alice = [pairs_to_key_int[i] for i in indices_comprobacion]
        print("Bits de comprobación Bob:", bits_comprobacion_enteros)
        print("Bits de comprobación Alice:", bits_comrpobacion_alice)
        if bits_comrpobacion_alice == bits_comprobacion_enteros:
            print("\nLas claves coinciden. La clave compartida es segura.")
         

        
            print("Clave compartida:",shared_key_str)
            print("Clave compartidad descodificada:", shared_key_bit)
            

            data = []
        
            conn1.close()
            server_socket3.close()
            server_socket9.close()

            server_socket4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
            server_socket4.bind(('localhost', 65480))
            server_socket4.listen(1)
            conn2, addr1 = server_socket4.accept()

        
            #listas de posiciones aleatorias de las bases coincidentes

            
        
            print("La clave compartida segura es:", key)
            shared_key = np.array(key)

            aes_key = derive_aes_key(shared_key.tobytes())
            print("Clave AES derivada:", aes_key.hex())

            def send_message():
                message = message_entry.get()
                message = message.encode()
                if message == b"exit":
                    conn2.close()
                    root.quit()
                else:
                    encrypted_message = encrypt_message(message, aes_key)
                    array_message = encrypted_message
        
                    conn2.sendall(pickle.dumps(array_message))
                    
                    
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    display_message(f"Yo - {timestamp}: {message.decode('utf-8')}")
                    print(f"Mensaje enviado: {message}")

            def receive_messages():
                while True:
                    try:
                        data = conn2.recv(1024)
                        if not data:
                            break
                        array_message = pickle.loads(data)
                        encrypted_message_received = array_message
                        ciphertext, tag, nonce = encrypted_message_received
                        decrypted_message = decrypt_message(ciphertext, aes_key, tag, nonce)
                        print(f"\033[1;32mMensaje recibido: {decrypted_message}\033[0m")
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        display_message(f"Bob - {timestamp}: {decrypted_message}")
                    except Exception as e:
                        print(f"Error al recibir mensaje: {e}")
                        break

            def display_message(message):
                message_display.config(state=tk.NORMAL)
                message_display.insert(tk.END, message + "\n")
                message_display.config(state=tk.DISABLED)
                message_display.see(tk.END)
            receive_thread = threading.Thread(target=receive_messages)
            receive_thread.start()

            root = tk.Tk()
            root.title("Alice - Enviar Mensaje")

                

                

            send_button = tk.Button(root, text="Enviar", command=send_message)
            send_button.pack(pady=20)

            message_display = tk.Text(root, state=tk.DISABLED, width=50, height=15)
            message_display.pack(pady=10)

            message_label = tk.Label(root, text="Escribe tu mensaje:")
            message_label.pack(pady=10)

            message_entry = tk.Entry(root, width=50)
            message_entry.pack(pady=10)

            def quit_and_close():
                conn2.close()
                server_socket1.close()
                server_socket2.close()
                server_socket3.close()
                root.destroy()
                os._exit(0)

            exit_button = tk.Button(root, text="Salir", command=quit_and_close)
            exit_button.pack(pady=5)
            root.mainloop()

            receive_thread.join()
        else:
            print("❌ ¡Intercambio de claves fallido!")
    # else:
    #         print("\nThe keys do not match. Potential interception detected.")
    #         print("Alice's subkey: ", alice_bits_seleccionados)
    #         print("Bob's subkey:   ", bob_bits_comprobacion)

        if conn:
            conn.close()
        if conn1:
            conn1.close()
        if conn2:
            conn2.close()
        if conn9:
            conn9.close()

        server_socket1.close()
        server_socket2.close()
        server_socket3.close()
        server_socket4.close()
        server_socket9.close()


    except KeyboardInterrupt:
        print("Servidor interrumpido por el usuario")
        if conn:
            conn.close()
        if conn1:
            conn1.close()
        if conn2:
            conn2.close()
        if conn9:
            conn9.close()
        server_socket1.close()
        server_socket2.close()
        server_socket3.close()
        server_socket4.close()
        server_socket9.close()


    finally:
        if conn2:
            conn2.close()
        if conn:
            conn.close()
        if conn1:
            conn1.close()
        if conn9:
            conn9.close()
        server_socket1.close()
        server_socket2.close()
        server_socket3.close()
        server_socket4.close()
        server_socket9.close()

        print("Socket cerrado")

start_sender()