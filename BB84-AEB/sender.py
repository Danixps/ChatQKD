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

# Función que intenta enlazar un socket
def bind_socket(server_socket, address, event, stop_event, conn_list):
    try:
        server_socket.bind(address)
        server_socket.listen(1)
        print(f"Esperando conexión en {address}...")

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


def decrypt_message(encrypted_message, aes_key):
    # Extraer el IV (primeros 16 bytes)
    iv = encrypted_message[:AES.block_size]
    ciphertext = encrypted_message[AES.block_size:]  # El resto es el mensaje cifrado
    
    # Crear el objeto de descifrado con el IV
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    
    # Intentar descifrar el mensaje
    try:
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)  # Eliminar padding
    except (ValueError, KeyError) as e:
        print("Error en el descifrado:", e)  # Imprimir error en caso de fallo
        return None
    
    return plaintext.decode()  # Decodificar el mensaje descifrado
# Función para derivar una clave AES a partir de la clave compartida
def derive_aes_key(shared_key):
    # Derivamos una clave de 16 bytes para AES-128
    key = hashlib.sha256(shared_key).digest()[:16]
    return key

# Función para cifrar el mensaje con AES
# Función de Alice para cifrar el mensaje
def encrypt_message(message, aes_key):
    # Crear un cipher con un IV aleatorio
    cipher = AES.new(aes_key, AES.MODE_CBC)
    # Asegurarse de que el mensaje está correctamente acolchonado
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    # Concatenar el IV con el mensaje cifrado
    
    return cipher.iv + ciphertext


def start_sender():
    conn = None
    conn1 = None
    connclose = None
    try:
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
        alice_bits = np.random.randint(2, size=30)  # Generar 30 bits aleatorios
        alice_bases = np.random.choice(['Z', 'X'], size=30)  # Bases aleatorias para cada bit
        print("Alice's bits: ", alice_bits)
        print("Alice's bases: ", alice_bases)

        circuits = []
        for i in range(30):
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

        # Recibir los circuitos de Eva
        data_length = conn1.recv(4)
        data_length = struct.unpack('!I', data_length)[0]
        data = b""
        while len(data) < data_length:
            packet = conn1.recv(4096)
            if not packet:
                break
            data += packet

        # Deserializar los circuitos
        received_circuits_bases = pickle.loads(data)
        bob_bases = received_circuits_bases
        print("Bases de Bob:", bob_bases)

        data_length1 = conn1.recv(4)
        data_length1 = struct.unpack('!I', data_length1)[0]
        data = b""
        while len(data) < data_length1:
            packet = conn1.recv(4096)
            if not packet:
                break
            data += packet
        received_circuits = pickle.loads(data)
        bob_results_bits = received_circuits
        print("Bits resultantes de Bob:", bob_results_bits)

        matching_bases = alice_bases == bob_bases
        print("Coincidencia en las bases:", matching_bases)

        bob_key = np.array(bob_results_bits)[matching_bases]
        alice_key = alice_bits[matching_bases]  # Seleccionar los bits de Alice donde las bases coinciden

            # Elegir una cantidad aleatoria de bits, mínimo 3 bits
        min_bits = 1
        num_bits = random.randint(min_bits, len(alice_key)-1)  # Número de bits aleatorios



        # Crear subconjuntos de bits
        alice_subkey = alice_key[:num_bits]
        bob_subkey = bob_key[:num_bits]
        bob_subkey2 = bob_key[num_bits:]

        # Comparar los subconjuntos
        if (alice_subkey == bob_subkey).all():
            print("\nThe key exchange was successful!")
            print("Alice's subkey:", alice_subkey)
            print("Bob's subkey: ", bob_subkey)
            result_key = np.concatenate(( bob_subkey, bob_subkey2))
            print("The complete key is:", result_key)
            # Crear una clave AES a partir de la clave compartida
            shared_key = np.concatenate((alice_key, bob_key))
            aes_key = derive_aes_key(shared_key)

            print("Clave AES generada:", aes_key)

            # Ahora, vamos a permitir que Alice y Bob se envíen mensajes cifrados
            def send_message():
                message = input("Escribe tu mensaje: ")
                if message == "exit":
                    conn.close()
                    return
                
                encrypted_message = encrypt_message(message, aes_key)
                array_aeskey_and_message = [aes_key, encrypted_message]
                conn1.sendall(pickle.dumps(array_aeskey_and_message))
            
                print(encrypted_message)
                decrypted_message = decrypt_message(encrypted_message, aes_key)
                print(f"Mensaje enviado: {decrypted_message} ")
                print("Mensaje enviado de forma segura.")

                # Recibir el mensaje cifrado de vuelta
                # encrypted_response = conn1.recv(1024)
                # decrypted_response = decrypt_message(encrypted_response, aes_key)
                # print(f"Mensaje recibido: {decrypted_response}")

            send_message()
        else:
            print("\nThe keys do not match. Potential interception detected.")
            print("Alice's subkey: ", alice_subkey)
            print("Bob's subkey:   ", bob_subkey)
        

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
