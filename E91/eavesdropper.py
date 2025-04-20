import socket

import struct
import socket
import numpy as np
import time
import random
import pickle
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

def start_reciever():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65458))
 
    conn = None
    try:

       
# Primero recibe 4 bytes para saber cuánto viene
        raw_size = b""
        while len(raw_size) < 4:
            packet = client_socket.recv(4 - len(raw_size))
            if not packet:
                raise ConnectionError("Conexión cerrada antes de recibir el tamaño.")
            raw_size += packet

        (data_length,) = struct.unpack('!I', raw_size)  # Desempaqueta el tamaño (un entero)

        # Ahora recibe exactamente data_length bytes
        data = b""
        while len(data) < data_length:
            packet = client_socket.recv(data_length - len(data))
            if not packet:
                raise ConnectionError("Conexión cerrada antes de recibir todos los datos.")
            data += packet

        # Finalmente convierte los bytes en una lista de enteros
        seeds = list(data)

        print(seeds)
        print("Número de semillas recibidas:", len(seeds))
        time.sleep(1)
        # Recibir los circuitos de Eva
        data = b""

        
     # Primero recibe el tamaño (4 bytes)
        data_len_bytes = client_socket.recv(4)
        data_length = struct.unpack('!I', data_len_bytes)[0]

        # Ahora recibe exactamente data_length bytes
        data = b''
        while len(data) < data_length:
            packet = client_socket.recv(data_length - len(data))
            if not packet:
                break
            data += packet

        received_circuits = pickle.loads(data)
        

        # Deserializar los circuitos

        

        eva_bits =[]
        # received_circuits = pickle.loads(data)
        # Diagnóstico: Imprimir el tipo y contenido de received_circuits
        
        
        # Generar bases aleatorias del mismo tamaño que los qubits recibidos

        num_qubits = len(seeds)
        eva_bases = np.random.choice(['X', 'Z'], size=num_qubits)
  
        circuits = received_circuits
        

        print("Bases de Eva:", eva_bases)

        
        for i in range(num_qubits):
        
            qc = circuits[i].copy()
            if eva_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X para medir si Bob usa la base X

            qc.measure(0, 0)  # Medir el qubit
            # Configurar el simulador con statevector
            backend = Aer.get_backend('qasm_simulator')
            compiled_circuit = transpile(qc, backend)
            job = backend.run(compiled_circuit, shots=1000, seed_simulator=seeds[i])  # <- semilla aquí
            result = job.result()
            counts = result.get_counts()

                        # Si solo estás midiendo el qubit 1 (como parece en tu código)
            most_common_bitstring = max(counts, key=counts.get)
            
            measured_bit = int(most_common_bitstring[-1])  # <- o [0] dependiendo del qubit



            eva_bits.append(measured_bit)

        print("Resultados de Eva:", eva_bits)
       

        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar el socket
        server_socket.bind(('localhost', 65431))
        server_socket.listen(1)
        conn, addr = server_socket.accept()
        # enviar los resultados de bob a alice
    
        # Enviar los resultados de Eva a Bob
        serialized_results = pickle.dumps(circuits)
      
        
        # Enviar la longitud de los datos primero
        data_length = len(seeds)
       
        # Enviar los resultados de Eva a Bob
        seeds = [random.randint(0, 255) for _ in range(data_length)]



        seeds_bytes = [bytes([x]) for x in seeds]

        conn.sendall(struct.pack('!I', len(seeds)))  # Envía primero el tamaño (4 bytes, formato network byte order)
        conn.sendall(b"".join(seeds_bytes))
        
        
        time.sleep(0.1)
        data_length = len(serialized_results)
        conn.sendall(struct.pack('!I', data_length))  # Envía primero el tamaño (4 bytes, formato network byte order)
        conn.sendall(serialized_results)    
 
        print("Resultados de Eva enviados a Bob")

      
        print("Bases de Eva enviadas a Bob")

        
        
        server_socket.close()
        conn.close()
        client_socket.close()
    except Exception as e:
        
        print(f"Error: {e}")
        if conn:
            conn.close()
        server_socket.close()
        client_socket.close()
    except KeyboardInterrupt:
   
        if conn:
            conn.close()
        server_socket.close()
        client_socket.close()
    finally:
        if conn:
            conn.close()
        client_socket.close()
        server_socket.close()
        print("Socket cerrado")


# Ejecutar el receptor
start_reciever()