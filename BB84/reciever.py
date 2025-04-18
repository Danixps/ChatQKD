import socket
import struct
import numpy as np
import pickle
import threading
from qiskit import transpile
from qiskit_aer import Aer
from Crypto.Cipher import AES
import hashlib
from datetime import datetime
import tkinter as tk

from Crypto.Random import get_random_bytes

import time
# Función para derivar una clave AES a partir de la clave compartida
def derive_aes_key(shared_key):
    # Derivamos una clave de 16 bytes para AES-128
    key = hashlib.sha256(shared_key).digest()[:16]
    return key

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

def encrypt_message(message, aes_key):
    nonce = get_random_bytes(12)  # Tamaño recomendado para GCM

    # Cifrado
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return [ciphertext, tag, nonce]

# Función para descifrar el mensaje con AES
def decrypt_message(encrypted_message, aes_key, tag, nonce):
    cipher_dec = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext_dec = cipher_dec.decrypt_and_verify(encrypted_message, tag)

    # Mostrar el mensaje descifrado
    return plaintext_dec.decode()

def start_receiver():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65431))
    
    try:
        # Recibir los datos serializados
        data_length = client_socket.recv(4)
        if not data_length:
            print("No se recibió la longitud de los datos de Eva")
            return
        data_length = struct.unpack('!I', data_length)[0]

        # Recibir los circuitos de Eva
        data = b""
        while len(data) < data_length:
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet

        # Deserializar los circuitos
        received_circuits = pickle.loads(data)
        
        # Generar bases aleatorias del mismo tamaño que los qubits recibidos
        num_qubits = len(received_circuits)
        bob_bases = np.random.choice(['X', 'Z'], size=num_qubits)
        print("Bases de Bob:", bob_bases)
        
        bob_result = []
        # Qubits de Alice a Bob
        circuits = received_circuits
        backend = Aer.get_backend('qasm_simulator')
        for i in range(num_qubits):
            # Crear una copia del circuito de Alice y medir en la base de Bob
            qc = circuits[i].copy()
            if bob_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X para medir si Bob usa la base X

            qc.measure(0, 0)  # Medir el qubit

            # Transpilar y ejecutar en el backend
            compiled_circuit = transpile(qc, backend)
            job = backend.run(compiled_circuit, shots=1)  # Ejecutar el circuito.

            result = job.result()
            measured_bit = int(list(result.get_counts().keys())[0])  # Obtener el bit medido
            bob_result.append(measured_bit)

        print("Resultados de Bob:", bob_result)

        # Serializar las bases de Bob
        client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket1.connect(('localhost', 65489))
        # Serializar los circuito
        serialized_bases = b"".join(bob_bases)
        
       
        client_socket1.sendall(serialized_bases)
    
        time.sleep(0.01)
        
        data = []
        # client_socket1.sendall(serialized_bits) ARREGLAR
        while len(data) < num_qubits:
            packet = client_socket1.recv(4096)
            if not packet:
                break
            data.append(packet)
        alice_bases_str = b"".join(data).decode()
        alice_bases = np.array(list(alice_bases_str))
        alice_bases = alice_bases[alice_bases != '']
        
        indices = alice_bases[-(num_qubits // 3):]  # Usamos `//` para división entera
        alice_bases = alice_bases[:num_qubits]
        
        
        print("Bases de Alice:", alice_bases)

        matching_bases = alice_bases == bob_bases
        bases_coincidentes = alice_bases[matching_bases]
      
        indices_comprobacion_enteros = [ord(x) for x in indices]
        print("Índices para comprobación:",  indices_comprobacion_enteros)

       # Verifica que bits_coincidentes tenga el tipo correcto
        bits_coincidentes = np.array(bob_result)[matching_bases]

        # Ahora, accede a los bits de comprobación usando índices enteros
        # Si `indices_comprobacion_enteros` tiene índices válidos para bits_coincidentes:
        bob_bits_seleccionados = [bits_coincidentes[i-1] for i in indices_comprobacion_enteros]

        print("Bits de comprobación:", bob_bits_seleccionados)





        
        client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket2.connect(('localhost', 65480))
        bob_bits_seleccionados_str = [str(x).encode() for x in bob_bits_seleccionados]
        client_socket2.sendall(b"".join(bob_bits_seleccionados_str))
      
        print ("Bits de comprobación enviados")
      
        matching_bases = alice_bases == bob_bases
        bases_coincidentes = bob_bases[matching_bases]
        print("Coincidencia en las bases:", matching_bases)
        print("Bases coincidentes:", bases_coincidentes)

        # Aquí Bob recibe la clave compartida y la utiliza para descifrar un mensaje (simulado)
        # Simulación de la clave derivada
        shared_key = np.array(bob_result)  # La clave compartida derivada de los resultados
        aes_key = derive_aes_key(shared_key.tobytes())  # Derivamos la clave AES

        data = client_socket2.recv(1024)  # Tamaño del buffer (ajústalo según sea necesario)
        array_aeskey_and_message = pickle.loads(data)

        # Extraer la clave AES y el mensaje cifrado
        aes_key_received, encrypted_message_received = array_aeskey_and_message
        ciphertext, tag, nonce = encrypted_message_received

        # Descifrar el mensaje
        decrypted_message = decrypt_message(ciphertext, aes_key_received, tag, nonce)
        if decrypted_message:
            # Código para imprimir en verde y negrita
        
            print(f"\033[1;32mMensaje descifrado: {decrypted_message}\033[0m")

        else:
            print("Error al descifrar el mensaje.")
       
                    # Ahora, vamos a permitir que Alice y Bob se envíen mensajes cifrados
  # Ahora, vamos a permitir que Alice y Bob se envíen mensajes cifrados
        def send_message():
            message = message_entry.get()
            message = message.encode()
            if message == b"exit":
                client_socket2.close()
                root.quit()
            else:
                encrypted_message = encrypt_message(message, aes_key)
                array_aeskey_and_message = [aes_key, encrypted_message]
                client_socket2.sendall(pickle.dumps(array_aeskey_and_message))
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                display_message(f"Yo    - {timestamp}: {message.decode('utf-8')}")
                print(f"Mensaje enviado: {message.decode('utf-8')}")

        def receive_messages():
            while True:
                try:
                    data = client_socket2.recv(1024)
                    if not data:
                        break
                    array_aeskey_and_message = pickle.loads(data)
                    aes_key_received, encrypted_message_received = array_aeskey_and_message
                    ciphertext, tag, nonce = encrypted_message_received
                    decrypted_message = decrypt_message(ciphertext, aes_key_received, tag, nonce)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    display_message(f"Alice - {timestamp}: {decrypted_message}")
                except Exception as e:
                    print(f"Error al recibir mensaje: {e}")
                    break

        def display_message(message):
            message_display.config(state=tk.NORMAL)
            message_display.insert(tk.END, message + "\n")
            message_display.config(state=tk.DISABLED)
            message_display.see(tk.END)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()

        root = tk.Tk()
        root.title("Bob - Enviar Mensaje")

        

        

        send_button = tk.Button(root, text="Enviar", command=send_message)
        send_button.pack(pady=20)

        message_display = tk.Text(root, state=tk.DISABLED, width=50, height=15)
        message_display.pack(pady=10)

        display_message(f"Alice - {timestamp}: {decrypted_message}")

        message_label = tk.Label(root, text="Escribe tu mensaje:")
        message_label.pack(pady=10)

        message_entry = tk.Entry(root, width=50)
        message_entry.pack(pady=10)

        def quit_and_close():
            root.destroy()
            client_socket2.close()

        exit_button = tk.Button(root, text="Salir", command=quit_and_close)
        exit_button.pack(pady=5)
        root.mainloop()

        receive_thread.join()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()
        client_socket1.close()
        client_socket2.close()
        print("Conexión cerrada")

# Ejecutar el receptor
start_receiver()