import socket
import numpy as np
import pickle
from qiskit import QuantumCircuit  
import struct
import random


def start_sender():
    conn = None
    conn1 = None

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 65458))
        server_socket.listen(1)
        print("Servidor en espera de conexión...")

        #programa de enviar qbits BB84
        # Convertir cada carácter a su valor ASCII y luego a binario
        alice_bits = np.random.randint(2, size=20)  # Generar 128 bits aleatorios
        n_bits = 20
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


        data_length = struct.pack('!I', len(serialized_circuits))
        conn.sendall(data_length)
        print(f"Conectado con {addr}")
        #como enviar algo a un sockety
        
        conn.sendall(serialized_circuits)
        
 

    
        server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket1.bind(('localhost', 65489))
        server_socket1.listen(1)
        conn1, addr1 = server_socket1.accept()
        print(f"Conectado con {addr1}")
        # Recibir los circuitos de Eva

        data_length = conn1.recv(4)
        data_length = struct.unpack('!I', data_length)[0]
        data = b""
        print("data_length", data_length)
        while len(data) < data_length:
            packet = conn1.recv(4096)
            if not packet:
                break
            data += packet
        # Deserializar los circuitos
        received_circuits_bases = pickle.loads(data)
        bob_bases = received_circuits_bases
        print("Bases de Bob:", bob_bases)

        data_length1= conn1.recv(4)
        data_length1= struct.unpack('!I', data_length1)[0]
        data = b""
        while len(data) < data_length1:
            packet = conn1.recv(4096)
            if not packet:
                break
            data += packet
        # Deserializar los circuitos
        received_circuits = pickle.loads(data)
        bob_results_bits = received_circuits
        print("Circuito de Bob:", bob_results_bits)



        matching_bases = alice_bases == bob_bases # Crear un array booleano de coincidencias


        print ("Coincidencia en las bases:", matching_bases)
 
        bob_key = np.array(bob_results_bits)[matching_bases]
        
        alice_key = alice_bits[matching_bases]  # Seleccionar los bits de Alice donde las bases coinciden


        alice_key_part1 = alice_key[:len(alice_key)//2]
        bob_key_part1 = bob_key[:len(bob_key)//2]
        bob_key_part2 = bob_key[len(bob_key)//2:]
        
        print ("Alice's key part 1:", alice_key_part1)
        print ("Bob's key part 1  :", bob_key_part1)


       # Validación de la clave
        if (alice_key_part1 == bob_key_part1).all():
            print("\nThe key exchange was successful!")
            bob_result_key = np.concatenate((bob_key_part1, bob_key_part2))
            print("The complete key is:", bob_result_key)
        else:
            print("\nThere is someone who tried to intercept the key!")



        
        
      
    


        
        
            
        
        
    except KeyboardInterrupt:
        print("Servidor interrumpido por el usuario")
    finally:
        if conn:
            conn.close()
        if conn1:
            conn1.close()
        server_socket.close()
        print("Socket cerrado")
        

# Ejecutar el servidor
start_sender()


