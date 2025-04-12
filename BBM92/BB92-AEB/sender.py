import socket
import threading
import numpy as np
import pickle
import struct
import random
from qiskit import QuantumCircuit
from Crypto.Cipher import AES
from qiskit import transpile
from datetime import datetime
import hashlib
from qiskit_aer import AerSimulator
import numpy as np
import tkinter as tk
import os
from qiskit_aer import Aer
from qiskit import QuantumCircuit
SIZE = 10

from qiskit.quantum_info import Statevector

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
                    print(f"Terminando espera en {address}")
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
        print(f"Conexión establecida exitosamente con: {conn.getpeername()}")

       

        alice_bases = np.random.choice(['Z', 'X'], size=SIZE)

      
        print("Alice's bases: ", alice_bases)
        circuits_bob = []
        alice_bits = []

        for i in range(SIZE):
            qc = QuantumCircuit(2, 2)
            qc.x([0, 1])
            qc.h(0)       # Hadamard en qubit 0 => lo pone en superposición
            qc.cx(0, 1)   # CNOT con control en qubit 0 y objetivo en qubit 1 => crea entrelazamiento

            circuits_bob.append(qc)
        seeds = [817234, 56298, 993201, 122345, 388822, 47291, 851024, 110099, 65287, 709350]

        serialized_circuits = pickle.dumps(circuits_bob)
        data_length = struct.pack('!I', len(serialized_circuits))
        conn.sendall(data_length)
        conn.sendall(serialized_circuits)
        print("Qubits enviados exitosamente.")

        for i in range(SIZE):
        # Alice mide su qubit
            qc = circuits_bob[i].copy()
            if alice_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X
            qc.measure(0, 0)  # Medir el qubit 0

            # Ejecutar la medición con simulador por defecto
            backend = Aer.get_backend('qasm_simulator')
            compiled_circuit = transpile(qc, backend)
            job = backend.run(compiled_circuit, shots=1000, seed_simulator=seeds[i])  # <- semilla aquí
            result = job.result()
            counts = result.get_counts()
          
                                # Si solo estás midiendo el qubit 1 (como parece en tu código)
            most_common_bitstring = max(counts, key=counts.get)
            
            measured_bit = int(most_common_bitstring[-1])  # <- o [0] dependiendo del qubit

            alice_bits.append(measured_bit)

        
        print("Resultados de Alice:", alice_bits)
        



        server_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       
        server_socket3.bind(('localhost', 65489))
        server_socket3.listen(1)
        conn1, addr1 = server_socket3.accept()
        print(f"Conectado con {addr1}")

        data = []
       
        while len(b"".join(data)) < SIZE:
            packet = conn1.recv(4096)
            if not packet:
                print("No se recibieron datos")
                break
            data.append(packet)


        bob_bases_str = b"".join(data).decode().strip()
        bob_bases = np.array(list(bob_bases_str))
        bob_bases = bob_bases[bob_bases != '']
        print("Bases de Bob:", bob_bases)
        
        send_alice_bases = b"".join(alice_bases)
        conn1.sendall(send_alice_bases )
        data = b""


       
        print("Alice's bases: ", alice_bases)
        matching_bases = alice_bases == bob_bases
        print("Coincidencia en las bases:", matching_bases)

        
                # Filtrar los índices donde las bases coinciden (esto te da los índices donde True en matching_bases)
        indices_coincidentes = np.array([i for i, match in enumerate(matching_bases) if match])
       

        # Ahora, puedes usar estos índices para extraer los bits correspondientes de alice_bits
        bits_coincidentes = [alice_bits[i] for i in indices_coincidentes]

        print("Índices para comprobación:", indices_coincidentes)
        print("bits_coincidentes:", bits_coincidentes)

        half_size = len(indices_coincidentes) // 2  # Tamaño de la mitad de los índices

        # Convierte indices_coincidentes en una lista y selecciona aleatoriamente
        indices_coincidentes_lista = indices_coincidentes.tolist()
        selected_indices = np.random.choice(indices_coincidentes_lista, SIZE//3, replace=False)

        print("Bits de comprbación", selected_indices)




        
        
        conn1.sendall(b"".join(selected_indices))
       
        data = []
        

   
        conn1.close()
        server_socket3.close()
        server_socket4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       
        server_socket4.bind(('localhost', 65480))
        server_socket4.listen(1)
        conn2, addr1 = server_socket4.accept()

        
       
        data = conn2.recv(1024)
           
     
        bob_bits_str = b"".join(bytes([x]) for x in data).decode()

        print ("Bits de comprobación recibidos", bob_bits_str)
        bob_bits_comprobacion = np.array(list(bob_bits_str), dtype=int)
       
        print("Bits de comprobación de Bob:",  bob_bits_comprobacion)




        #listas de posiciones aleatorias de las bases coincidentes


     



        

        alice_bits_seleccionados = np.array([alice_bits[i] for i in selected_indices])
        print (alice_bits_seleccionados)

        if np.array_equal(alice_bits_seleccionados, bob_bits_comprobacion):
            print("Intercambio de claves exitoso")
            print("\nThe key exchange was successful!")
            print("Alice's subkey:", alice_bits_seleccionados)
            print("Bob's subkey: ", bob_bits_comprobacion)
            print ("Los bits coincidentes son: ", bits_coincidentes)
            #quiitar a bits_coincidentes los bits de comprobación
           
            key = [x for i, x in enumerate(bits_coincidentes) if i not in indices_coincidentes-1]
            print("The complete key is:", key)
           
            aes_key = derive_aes_key(bytes(key))

            def send_message():
                message = message_entry.get()
                message = message.encode()
                if message == b"exit":
                    conn2.close()
                    root.quit()
                else:
                    encrypted_message = encrypt_message(message, aes_key)
                    array_aeskey_and_message = [aes_key, encrypted_message]
                    conn2.sendall(pickle.dumps(array_aeskey_and_message))
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    display_message(f"Yo - {timestamp}: {message.decode('utf-8')}")
                    print(f"Mensaje enviado: {message}")

            def receive_messages():
                while True:
                    try:
                        data = conn2.recv(1024)
                        if not data:
                            break
                        array_aeskey_and_message = pickle.loads(data)
                        aes_key_received, encrypted_message_received = array_aeskey_and_message
                        ciphertext, tag, nonce = encrypted_message_received
                        decrypted_message = decrypt_message(ciphertext, aes_key_received, tag, nonce)
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
            print("\nThe keys do not match. Potential interception detected.")
            print("Alice's subkey: ", selected_indices)
            print("Bob's subkey:   ", bob_bits_comprobacion)

        if conn:
            conn.close()
        if conn1:
            conn1.close()
        if conn2:
            conn2.close()

        server_socket1.close()
        server_socket2.close()
        server_socket3.close()
        server_socket4.close()


    except KeyboardInterrupt:
        print("Servidor interrumpido por el usuario")
        if conn:
            conn.close()
        if conn1:
            conn1.close()
        if conn2:
            conn2.close()
        server_socket1.close()
        server_socket2.close()
        server_socket3.close()
        server_socket4.close()


    finally:
        if conn2:
            conn2.close()
        if conn:
            conn.close()
        if conn1:
            conn1.close()
        server_socket1.close()
        server_socket2.close()
        server_socket3.close()
        server_socket4.close()

        print("Socket cerrado")

start_sender()