import socket
import struct
import numpy as np
import pickle
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

# Función para derivar una clave AES a partir de la clave compartida
def derive_aes_key(shared_key):
    # Derivamos una clave de 16 bytes para AES-128
    key = hashlib.sha256(shared_key).digest()[:16]
    return key

# Función para descifrar el mensaje con AES
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
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
        # Serializar los circuitos
        serialized_bases = pickle.dumps(bob_bases)
        serialized_circuits = pickle.dumps(bob_result)
        data_length = struct.pack('!I', num_qubits)
        client_socket1.sendall(data_length)
        client_socket1.sendall(serialized_bases)
        import time
        time.sleep(1)
        data_length = struct.pack('!I', num_qubits)
        client_socket1.sendall(data_length)
        client_socket1.sendall(serialized_circuits)

        # Aquí Bob recibe la clave compartida y la utiliza para descifrar un mensaje (simulado)
        # Simulación de la clave derivada
        shared_key = np.array(bob_result)  # La clave compartida derivada de los resultados
        aes_key = derive_aes_key(shared_key.tobytes())  # Derivamos la clave AES

        data = client_socket1.recv(1024)  # Tamaño del buffer (ajústalo según sea necesario)
        array_aeskey_and_message = pickle.loads(data)

        # Extraer la clave AES y el mensaje cifrado
        aes_key_received, encrypted_message_received = array_aeskey_and_message
        print (aes_key_received)
        print (encrypted_message_received)
        # Descifrar el mensaje
        decrypted_message = decrypt_message(encrypted_message_received, aes_key_received)
        if decrypted_message:
            print(f"Mensaje descifrado: {decrypted_message}")
        else:
            print("Error al descifrar el mensaje.")
        client_socket.close()
        client_socket1.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()
        client_socket1.close()
        print("Conexión cerrada")

# Ejecutar el receptor
start_receiver()
