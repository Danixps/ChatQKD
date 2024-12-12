import socket

import struct
import socket
import numpy as np
import pickle
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

def start_reciever():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65452))
    
    try:

        # Recibir los datos serializados
        data_length = client_socket.recv(4)
        if not data_length:
            print("No se recibió la longitud de los datos de Alice")
            return
        data_length = struct.unpack('!I', data_length)[0]

    # Recibir los circuitos de Alice
        data = b""
        while len(data) < data_length:
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet

        # Deserializar los circuitos
        received_circuits = pickle.loads(data)
        bob_results = []
        # Generar bases aleatorias del mismo tamaño que los qubits recibidos
        num_qubits = len(received_circuits)
        bob_bases = np.random.choice(['X', 'Z'], size=num_qubits)
        print("Bases de Bob:", bob_bases)
        #qbits de alice a bob
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
            bob_results.append(measured_bit)

        print("Bob's bits results:", bob_results)
        # enviar los resultados de bob a alice
        serialized_results = pickle.dumps(bob_results)
        serialized_bases_bob = pickle.dumps(bob_bases)
  
        
    
        print ("Enviando bases a Alices")
        client_socket.sendall(serialized_bases_bob)
        print("Resultados enviados a Alice")
        client_socket.sendall(serialized_results)

       
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Conexión cerrada")

# Ejecutar el receptor
start_reciever()