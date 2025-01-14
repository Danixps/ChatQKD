import socket
import threading
import numpy as np
import pickle
import struct
import random
from qiskit import QuantumCircuit
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import hashlib
import tkinter as tk
from tkinter import messagebox
# Función que intenta enlazar un socket
SIZE=30
def bind_socket(server_socket, address, event, stop_event, conn_list):
    try:
        server_socket.bind(address)
        server_socket.listen(1)

        # Esperar conexión si el evento global no está activado
        while not event.is_set():
            server_socket.settimeout(1)  # Tiempo de espera de 1 segundo
            try:
                conn, addr = server_socket.accept()
                print(f"Conexión aceptada en {address}")
                conn_list.append(conn)
                event.set()  # Indica que una conexión fue exitosa
                break
            except socket.timeout:
                if stop_event.is_set():  # Detener si otro socket ya conectó
                    print(f"Terminando espera en {address}")
                    break
    except Exception as e:
        print(f"Error en {address}: {e}")
    finally:
        server_socket.close()


def decrypt_message(encrypted_message, aes_key, tag, nonce):
    cipher_dec = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext_dec = cipher_dec.decrypt_and_verify(encrypted_message, tag)

    # Mostrar el mensaje descifrado
    return plaintext_dec.decode()

# Función para derivar una clave AES a partir de la clave compartida
def derive_aes_key(shared_key):
    # Derivamos una clave de 16 bytes para AES-128
    key = hashlib.sha256(shared_key).digest()[:16]
    return key

# Función para cifrar el mensaje con AES
# Función de Alice para cifrar el mensaje
def encrypt_message(message, aes_key):
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    nonce = get_random_bytes(12)  # Tamaño recomendado para GCM

    # Cifrado
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(message)
    return [ciphertext, tag, nonce]


def start_sender():
    conn = None
    conn1 = None
    connclose = None
    try:
        print(f"Esperando conexión...")
        # Crear eventos para coordinar hilos
        connection_event = threading.Event()
        stop_event = threading.Event()
        conn_list = []

        # Crear sockets para los dos puertos
        server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Crear hilos para escuchar en los dos puertos
        thread1 = threading.Thread(target=bind_socket, args=(server_socket1, ('localhost', 65431), connection_event, stop_event, conn_list))
        thread2 = threading.Thread(target=bind_socket, args=(server_socket2, ('localhost', 65458), connection_event, stop_event, conn_list))

        thread1.start()
        thread2.start()

        # Esperar a que uno de los hilos establezca conexión
        connection_event.wait()

        # Indicar a los otros hilos que deben detenerse
        stop_event.set()

        # Esperar a que ambos hilos terminen
        thread1.join()
        thread2.join()

        # Tomar la conexión establecida
        conn = conn_list[0]
        print(f"Conexión establecida exitosamente con: {conn.getpeername()}")

        # Simulación del envío de bits BB84
        alice_bits = np.random.randint(2, size=SIZE)  # Generar 30 bits aleatorios
        alice_bases = np.random.choice(['Z', 'X'], size=SIZE)  # Bases aleatorias para cada bit
        print("Alice's bits: ", alice_bits)
        print("Alice's bases: ", alice_bases)

        circuits = []
        for i in range(SIZE):
            qc = QuantumCircuit(1, 1)
            if alice_bits[i] == 1:
                qc.x(0)
            if alice_bases[i] == 'X':
                qc.h(0)
            circuits.append(qc)

        serialized_circuits = pickle.dumps(circuits)
        data_length = struct.pack('!I', len(serialized_circuits))
        conn.sendall(data_length)
        conn.sendall(serialized_circuits)
        print("Qubits enviados exitosamente.")

        server_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket3.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket3.bind(('localhost', 65489))
        server_socket3.listen(1)
        conn1, addr1 = server_socket3.accept()
        print(f"Conectado con {addr1}")


        data = []
        data_length1 = SIZE
        while len(b"".join(data)) < SIZE:
            packet = conn1.recv(4096)
            if not packet:
                print("No se recibieron datos")
                break
            data.append(packet)
        print("Datos recibidos: ", len(b"".join(data)), "byt")
        # Deserializar los circuitos
        # Decodificar los datos y convertirlos en un array de numpy
        bob_bases_str = b"".join(data).decode()
        bob_bases_str = bob_bases_str.strip()
        print ("Bob's bases: ", bob_bases_str)
        # Extracción de la parte relevante (después de los dos puntos)
   

        # Conversión a un array de caracteres en NumPy
        bob_bases = np.array(list(bob_bases_str))
        #quitar los vacios
        bob_bases = bob_bases[bob_bases != '']

        print("Bases de Bob:", bob_bases)

        data = b""
        while len(data) < SIZE:
            packet = conn1.recv(4096)
            if not packet:
                break
            data += packet
        bob_results_str = data.decode()
        bob_results_bits = np.array(list(bob_results_str)).astype(int)
        print("Bob's results:", bob_results_str)
        print("Bits resultantes de Bob:", bob_results_bits)
        print ("Bob's bases: ", bob_bases)
        print ("Alice's bases: ", alice_bases)
        matching_bases = alice_bases == bob_bases
        print("Coincidencia en las bases:", matching_bases)

        bob_key = bob_results_bits[matching_bases]
        alice_key = alice_bits[matching_bases]  # Seleccionar los bits de Alice donde las bases coinciden

            # Elegir una cantidad aleatoria de bits, mínimo 3 bits
        min_bits = 1
        num_bits = random.randint(min_bits, len(alice_key)-1)  # Número de bits aleatorios



        # Asegurarnos de que num_bits no sea mayor que la longitud de las claves
        num_bits = min(num_bits, len(alice_key), len(bob_key))

        # Generar índices aleatorios para los subconjuntos
        # Crear subconjunto de Alice
        alice_indices = random.sample(range(len(alice_key)), num_bits)  # Generar num_bits índices aleatorios para alice_key

        # Crear subconjunto de Bob
        bob_indices = random.sample(range(len(bob_key)), num_bits)  # Generar num_bits índices aleatorios para bob_key

        # Crear los subconjuntos seleccionando los bits usando los índices aleatorios
        alice_subkey = ''.join([str(alice_key[i]) for i in sorted(alice_indices)])
        bob_subkey = ''.join([str(bob_key[i]) for i in sorted(alice_indices)])

        # Segunda parte de la subclave de Bob (el complemento de los índices aleatorios)
        remaining_bob_indices = list(set(range(len(bob_key))) - set(alice_indices))
        bob_subkey2 = ''.join([str(bob_key[i]) for i in sorted(remaining_bob_indices)])
        # Comparar los subconjuntos
        if alice_subkey == bob_subkey:
            print("\nThe key exchange was successful!")
            print("Alice's subkey:", alice_subkey)
            print("Bob's subkey: ", bob_subkey)
            result_key = bob_subkey2
            print("The complete key is:", result_key)
            # Crear una clave AES a partir de la clave compartida
            shared_key = np.concatenate((alice_key, bob_key))
            aes_key = derive_aes_key(shared_key)

    

            # Ahora, vamos a permitir que Alice y Bob se envíen mensajes cifrados
            def send_message():
                # Obtener el mensaje del cuadro de texto
                message = message_entry.get()
                message = message.encode()
                if message == "exit":
                    # Si el mensaje es "exit", cerramos la conexión y salimos
                    conn1.close()
                    root.quit()
                else:
                    # Cifrar el mensaje
                    encrypted_message = encrypt_message(message, aes_key)
                    # Empaquetar la clave AES y el mensaje cifrado en una lista
                    array_aeskey_and_message = [aes_key, encrypted_message]
                    # Enviar el mensaje cifrado y la clave AES a través de la conexión
                    conn1.sendall(pickle.dumps(array_aeskey_and_message))  
                    print(f"Mensaje enviado: {message}")
                
                    # Recibir el mensaje cifrado de vuelta
                    # encrypted_response = conn1.recv(SIZE)
                    # decrypted_response = decrypt_message(encrypted_response, aes_key)
                    # print(f"Mensaje recibido: {decrypted_response}")
                    root.destroy()  # Cierra la ventana
            # Configuración de la interfaz gráfica
            root = tk.Tk()
            root.title("Alice - Enviar Mensaje")

            message_label = tk.Label(root, text="Escribe tu mensaje:")
            message_label.pack(pady=10)

            message_entry = tk.Entry(root, width=50)
            message_entry.pack(pady=10)

            send_button = tk.Button(root, text="Enviar", command=send_message )
            send_button.pack(pady=20)

            exit_button = tk.Button(root, text="Salir", command=root.quit)
            exit_button.pack(pady=5)
            root.mainloop()
            data = conn1.recv(1024)  # Tamaño del buffer (ajústalo según sea necesario)
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
        else:
            print("\nThe keys do not match. Potential interception detected.")
            print("Alice's subkey: ", alice_subkey)
            print("Bob's subkey:   ", bob_subkey)
            conn.close()
            conn1.close()
            server_socket1.close()
            server_socket2.close()
            server_socket3.close()



        conn.close()
        conn1.close()
        server_socket1.close()
        server_socket2.close()
        server_socket3.close()

    except KeyboardInterrupt:
        print("Servidor interrumpido por el usuario")

        if conn:
            conn.close()
        if conn1:
            conn1.close()

        server_socket1.close()
        server_socket2.close()
        server_socket3.close()

    finally:
        if conn:
            conn.close()
        if conn1:
            conn1.close()
        server_socket1.close()
        server_socket2.close()
        server_socket3.close()

        print("Socket cerrado")

# Ejecutar el servidor
start_sender()