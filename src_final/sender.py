import socket
import numpy as np
import pickle
from qiskit import QuantumCircuit  
import time


def start_sender():
    conn = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 65451))
        server_socket.listen(1)
        print("Servidor en espera de conexión...")

        #programa de enviar qbits BB84
        # Convertir cada carácter a su valor ASCII y luego a binario
        alice_bits = np.random.randint(2, size=10)  # Generar 128 bits aleatorios
        n_bits = 10
        # alice genera aleatoriamente las bases para cada bit (elige entre 'Z' o 'X')
        alice_bases = np.random.choice(['Z', 'X'], size=n_bits)
        print ("Alice's bits: ", alice_bits)
        print ("Alice's bases: ", alice_bases)

        # Codifico los bits y bases de Alice en qbits
        # Alice codifica los bits en qubits y los envía a Bob
        circuits = []  # Lista para almacenar los circuitos cuánticos que representa cada qubit enviado

        for i in range(n_bits):
            qc = QuantumCircuit(1, 1)

            # Preparar el estado basado en el bit y la base de Alice
            if alice_bits[i] == 1:
                qc.x(0)  # Aplicar puerta X si el bit de Alice es 1


            if alice_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X si la base de Alice es 1 (estados superposicion si es un 1 lo convierte en un | - > y si es un 0 en un | + >)

            circuits.append(qc)

        # Ahora tenemos los qubits de Alice
        

        # Serializar los circuitos
        serialized_circuits = pickle.dumps(circuits)

        
        conn, addr = server_socket.accept()
        print(f"Conectado con {addr}")
        #como enviar algo a un sockety
        
        conn.sendall(serialized_circuits)
    
        
            
        
        
    except KeyboardInterrupt:
        print("Servidor interrumpido por el usuario")
    finally:
        if conn:
            conn.close()
        server_socket.close()
        print("Socket cerrado")
        

# Ejecutar el servidor
start_sender()


