import socket
import struct
import numpy as np
import random
import pickle
import threading
import ast
from qiskit import transpile
import re
from qiskit_aer import Aer
from Crypto.Cipher import AES
from qiskit.quantum_info import Statevector
import hashlib
from datetime import datetime
import tkinter as tk


from Crypto.Random import get_random_bytes

import time

def identify_state(sv, tol=1e-6):
    states = {
        '0': np.array([1, 0]),
        '1': np.array([0, 1]),
        '+': np.array([1/np.sqrt(2), 1/np.sqrt(2)]),
        '-': np.array([1/np.sqrt(2), -1/np.sqrt(2)])
    }
    for label, ref in states.items():
        if np.allclose(sv.data, ref, atol=tol):
            return label
    return '?'  # Si no se reconoce

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
        data_length_states = client_socket.recv(4)
        if not data_length_states:
            print("No se recibió la longitud de los datos de Eva")
            return
        data_length_states = struct.unpack('!I', data_length_states)[0]

        
        received_circuits = pickle.loads(data)
        data = b""
        while len(data) < data_length_states:
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet
        pairs_alice_bytes = data
        
        pairs_alice = pairs_alice_bytes.decode('utf-8')
        
        # Usar una expresión regular para agregar comas entre las tuplas
        data_str = re.sub(r"(\)\()", r"),(", pairs_alice)

        # Convertir la cadena en una lista de tuplas usando ast.literal_eval
        pairs_list = ast.literal_eval(f"[{data_str}]")


        # Imprimir los resultados
        print("Pares de estado enviados de Alice:", pairs_list)
       
        # Generar bases aleatorias del mismo tamaño que los qubits recibidos
        num_qubits = len(received_circuits)
        bob_bases = np.random.choice(['X', 'Z'], size=num_qubits)
        print("Bases de Bob:", bob_bases)
        
        bob_result = []
        array_states = []
        result =[]
        index =[]
        key = []
        # Qubits de Alice a Bob
        circuits = received_circuits
        backend = Aer.get_backend('qasm_simulator')
        for i in range(num_qubits):
            # Crear una copia del circuito de Alice y medir en la base de Bob
            qc = circuits[i].copy()
            random_base = random.choice(['C', 'H']) #Elecion random de aplicar hadamard adamard o comutacional
            if random_base == 'H':
                qc.h(0)
            qc.measure(0, 0)  # Medir el qubit

            # Transpilar y ejecutar en el backend
            compiled_circuit = transpile(qc, backend)
            job = backend.run(compiled_circuit, shots=1)  # Ejecutar el circuito.

            resultado = job.result()
            measured_bit = int(list(resultado.get_counts().keys())[0])  # Obtener el bit medido
            
            # print(sv)
            # Identificar el estado antes de la medición
          
         
            # # # Aplicar la puerta Hadamard o Comutacional según la base de Bob
            # print(f"medición: {measured_bit}, index: {i}, base: {random_base}")
            # # print(f"Estado antes de la medición: {pairs_list[i][1]}, medición: {measured_bit}")

           
                # print(f"Aplicando Hadamard, estado antes de la medición: {pairs_list[i][0]}, medición: {measured_bit}")
            if pairs_list[i][0] == '0' and pairs_list[i][1] == '-' and random_base == 'H'and measured_bit == 1: # caso de que el estado sea  0
                result.append(pairs_list[i][1])
                index.append(i)
                if pairs_list[i][1] == '+':
                    key.append(1)
                else:
                    key.append(0)
            elif pairs_list[i][0] == '1' and pairs_list[i][1] != '-' and random_base == 'H' and measured_bit == 0: #caso de que el estado sea 1
                result.append(pairs_list[i][1])
                index.append(i)
                if pairs_list[i][1] == '+':
                    key.append(1)
                else:
                    key.append(0)
            

        
                # print(f"Aplicando Computacional, estado antes de la medición: {pairs_list[i][0]}, medición: {measured_bit}")
            elif pairs_list[i][1] == '+' and pairs_list[i][0] != '1' and random_base == 'C' and measured_bit == 1:
                result.append(pairs_list[i][0])
                index.append(i)
                if pairs_list[i][0] == '0':
                    key.append(0)
                else:
                    key.append(1)
                    
            elif pairs_list[i][1] == '-' and pairs_list[i][0] != '0' and random_base == 'C' and measured_bit == 0:
                result.append(pairs_list[i][0])
                index.append(i)
                if pairs_list[i][0] == '0':
                    key.append(0)



           
                
         
            
            
            
            
            
            # print(sv)
            # Identificar el estado antes de la medición
          
            # if (state != pairs_list[i][0] and state == '1'):
            #     result.append(pairs_list[i][0])
            #     index.append(i)
            #     qc.measure(0, 0)
            #     key.append(qc)

            # elif (state != pairs_list[i][0] and state == '0'):
            #     result.append(pairs_list[i][0])
            #     index.append(i)
            #     qc.measure(0, 0)
            #     key.append(qc)
            # elif (state != pairs_list[i][1] and state == '-'):
            #     result.append(pairs_list[i][1])
            #     index.append(i)
            #     qc.measure(0, 0)
            #     key.append(qc)
            # elif (state != pairs_list[i][1] and state == '+'):
            #     result.append(pairs_list[i][1])
            #     index.append(i)
            #     qc.measure(0, 0)
            #     key.append(qc)
            
           
            
            

            
            
            # if bob_bases[i] == 'X':
            #     qc.h(0)  # Cambiar a la base X para medir si Bob usa la base X

            # qc.measure(0, 0)  # Medir el qubit

            # # Transpilar y ejecutar en el backend
            # compiled_circuit = transpile(qc, backend)
            # job = backend.run(compiled_circuit, shots=1)  # Ejecutar el circuito.

            # result = job.result()
            # measured_bit = int(list(result.get_counts().keys())[0])  # Obtener el bit medido
            # bob_result.append(measured_bit)

        # print("Resultados de Bob:", bob_result)
        print("Indices de resultados de todos qbits:", array_states)
        print("Indices de resultados:", index)
        print("Resultados:", result)
        
        # Serializar las bases de Bob
        client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket1.connect(('localhost', 65489))
        # Serializar los circuito


        
        #### index_str = bytes(index)
        index_str = b"".join(struct.pack('!i', index) for index in index)
        
        time.sleep(1)
        client_socket1.sendall(index_str)
    
       
        #################
        ################
        ################
        ################
        ################
        ################
        ################
        ################
        ################
        ################


        shared_key_bit = ['0' if x == '+' else '1' if x == '-' else x for x in result]
        client_socket1.close()
        time.sleep(1)
        client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket2.connect(('localhost', 65480))
        print("Clave compartidad descodificada:", shared_key_bit)
        
      
      
       
  

        # Aquí Bob recibe la clave compartida y la utiliza para descifrar un mensaje (simulado)
        # Simulación de la clave derivada
        shared_key = np.array(shared_key_bit)
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