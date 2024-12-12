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
    client_socket.connect(('localhost', 65454))
 
    conn = None
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
        eva_bits = []
        # Generar bases aleatorias del mismo tamaño que los qubits recibidos
        num_qubits = len(received_circuits)
        eva_bases = np.random.choice(['X', 'Z'], size=num_qubits)
        print("Bases de Eva:", eva_bases)
        
        circuits = received_circuits
        backend = Aer.get_backend('qasm_simulator')
        for i in range(num_qubits):
        # Crear una copia del circuito de Alice y medir en la base de Eva
            qc = circuits[i].copy()
            if eva_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X para medir si Eva usa la base X

            qc.measure(0, 0)  # Medir el qubit

            # Transpilar y ejecutar en el backend
            compiled_circuit = transpile(qc, backend)
            job = backend.run(compiled_circuit, shots=1) # devuelve los resultados de la ejecución del circuito.

            result = job.result()
            measured_bit = int(list(result.get_counts().keys())[0])  # Obtener el bit medido
            eva_bits.append(measured_bit)

        print("Eva's bits results:", eva_bits)
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 65457))
        server_socket.listen(1)
        conn, addr = server_socket.accept()
        # enviar los resultados de bob a alice
        serialized_results = pickle.dumps(eva_bits)
        serialized_bases_bob = pickle.dumps(eva_bases)
  
        # Bob mide los qubits que recibe de Alice
        backend = Aer.get_backend('qasm_simulator')

        # Asegurarse de que eva_bits esté vacío al inicio
    
        circuits_eva = []  # Lista para almacenar los circuitos cuánticos que representa cada qubit enviado
        for i in range(num_qubits):
            qc = QuantumCircuit(1, 1)

            # Preparar el estado basado en el bit y la base de Alice
            if eva_bits[i] == 1:
                qc.x(0)  # Aplicar puerta X si el bit de Alice es 1


            if eva_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X si la base de Alice es 1 (estados superposicion si es un 1 lo convierte en un | - > y si es un 0 en un | + >)

            circuits_eva.append(qc)
            circuits = circuits_eva
    
        print ("Enviando bases a Alices")
        data_length = struct.pack('!I', len(circuits))
        conn.sendall(data_length)
    
        data_length1 = struct.pack('!I', circuits))
        conn.sendall(data_length1)

        print("Bases de Eva enviadas a Bob")

        conn.close()
        server_socket.close()
        client_socket.close()

       
    except Exception as e:
        
        print(f"Error: {e}")
        conn.close()
        server_socket.close()
        client_socket.close()



# Ejecutar el receptor
start_reciever()