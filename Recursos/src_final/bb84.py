

# Importar bibliotecas necesarias de Qiskit y otras de Python
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

# Alice genera una clave aleatoria
# Mensaje en texto claro
def simulate_bb84() :
    eva_flag = False

    # Convertir cada carácter a su valor ASCII y luego a binario
    alice_bits = np.random.randint(2, size=250)  # Generar 128 bits aleatorios
    n_bits =250
    # Mostrar el mensaje en binario
    print("Mensaje en binario:", alice_bits)

    # alice genera aleatoriamente las bases para cada bit (elige entre 'Z' o 'X')
    alice_bases = np.random.choice(['Z', 'X'], size=n_bits)


    print ("Alice's bits: ", alice_bits)
    print ("Alice's bases: ", alice_bases)

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

    
    if eva_flag == True:
    # Eva elige aleatoriamente sus bases de medición
        eva_bases = np.random.choice(['Z', 'X'], size=n_bits)
        eva_bits = []
        print ("Alice's bits: ", alice_bits)
        print ("Alice's bases: ", alice_bases)
        print ("Eva's bases: ", eva_bases)

        # Bob mide los qubits que recibe de Alice
        backend = Aer.get_backend('qasm_simulator')

        # Asegurarse de que bob_results esté vacío al inicio
        bob_results = []

        for i in range(n_bits):
            # Crear una copia del circuito de Alice y medir en la base de Bob
            qc = circuits[i].copy()
            if eva_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X para medir si Bob usa la base X

            qc.measure(0, 0)  # Medir el qubit

            # Transpilar y ejecutar en el backend
            compiled_circuit = transpile(qc, backend)
            job = backend.run(compiled_circuit, shots=1) # devuelve los resultados de la ejecución del circuito.

            result = job.result()
            measured_eva_bit = int(list(result.get_counts().keys())[0])  # Obtener el bit medido
            eva_bits.append(measured_eva_bit)

            circuits_eva = []  # Lista para almacenar los circuitos cuánticos que representa cada qubit enviado

        print ("Eva's bit: ", eva_bits)
        for i in range(n_bits):
            qc = QuantumCircuit(1, 1)

            # Preparar el estado basado en el bit y la base de Alice
            if eva_bits[i] == 1:
                qc.x(0)  # Aplicar puerta X si el bit de Alice es 1


            if eva_bases[i] == 'X':
                qc.h(0)  # Cambiar a la base X si la base de Alice es 1 (estados superposicion si es un 1 lo convierte en un | - > y si es un 0 en un | + >)

            circuits_eva.append(qc)
            circuits = circuits_eva

        # Bob elige aleatoriamente sus bases de medición
    bob_bases = np.random.choice(['Z', 'X'], size=n_bits)
    bob_results = []
    print ("Bob's bases: ", bob_bases)

    # Bob mide los qubits que recibe de Alice
    backend = Aer.get_backend('qasm_simulator')

    # Asegurarse de que bob_results esté vacío al inicio
    bob_results = []

    for i in range(n_bits):
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

    # Alice y Bob comparan sus bases públicamente
    matching_bases = alice_bases == bob_bases  # Crear un array booleano de coincidencias
    print ("Alice's bases:", alice_bases)
    print ("Bob's bases  :", bob_bases)
    print ("Matching bases:", matching_bases)

    # Usar el enmascarado booleano para seleccionar los bits coincidentes de Alice y Bob es decir despreciar los bits que no tengan misma base
    alice_key = alice_bits[matching_bases]  # Seleccionar los bits de Alice donde las bases coinciden

    bob_key = np.array(bob_results)[matching_bases]  # Seleccionar los resultados de Bob donde las bases coinciden

    alice_key_part1 = alice_key[:len(alice_key)//2]
    bob_key_part1 = bob_key[:len(bob_key)//2]
    bob_key_part2 = bob_key[len(bob_key)//2:]

    print ("Alice's key part 1:", alice_key_part1)
    print ("Bob's key part 1  :", bob_key_part1)

    if (alice_key_part1 == bob_key_part1).all():
        print("\nThe key exchange was successful!")
        bob_result_key = np.concatenate((bob_key_part1, bob_key_part2))
        bob_result_key = bob_result_key[:128]
        bob_result_key_bits = ''.join(str(int(c)) for c in bob_result_key)
        bob_result_key_bits = bob_result_key_bits.ljust(128, '0')  # Rellenar con ceros a la derecha si es necesario
        print(f'bob_result_key in 128 bits: {bob_result_key_bits}')
          # Escribir la clave en un fichero
        with open('shared_key.temp', 'w') as f:
            f.write(bob_result_key_bits)
    else:
        print("\nThere is someone who tried to intercept the key!")
        