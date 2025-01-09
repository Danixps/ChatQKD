import socket
import struct
import numpy as np
import pickle
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

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
            job = backend.run(compiled_circuit, shots=1) # devuelve los resultados de la ejecución del circuito.

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