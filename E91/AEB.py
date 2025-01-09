

# Useful additional packages 
import numpy as np
import random
# Regular expressions module
import re
import matplotlib.pyplot as plt

# Importing the Qiskit libraries
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

# Import basic plot tools


def start_sender():
    
    # Create quantum and classical registers
    qr = QuantumRegister(2, name="qr")
    cr = ClassicalRegister(4, name="cr")

    # Create singlet state circuit
    singlet = QuantumCircuit(qr, cr, name='singlet')
    singlet.x(qr[0])
    singlet.x(qr[1])
    singlet.h(qr[0])
    singlet.cx(qr[0], qr[1])

    ## Alice's measurement circuits
    # Measure Alice's qubit in the X basis
    measureA1 = QuantumCircuit(qr, cr, name='measureA1')
    measureA1.h(qr[0])
    measureA1.measure(qr[0], cr[0])

    # Measure Alice's qubit in the W basis
    measureA2 = QuantumCircuit(qr, cr, name='measureA2')
    measureA2.s(qr[0])
    measureA2.h(qr[0])
    measureA2.t(qr[0])
    measureA2.h(qr[0])
    measureA2.measure(qr[0], cr[0])

    # Measure Alice's qubit in the Z basis
    measureA3 = QuantumCircuit(qr, cr, name='measureA3')
    measureA3.measure(qr[0], cr[0])

    ## Bob's measurement circuits
    # Measure Bob's qubit in the W basis
    measureB1 = QuantumCircuit(qr, cr, name='measureB1')
    measureB1.s(qr[1])
    measureB1.h(qr[1])
    measureB1.t(qr[1])
    measureB1.h(qr[1])
    measureB1.measure(qr[1], cr[1])

    # Measure Bob's qubit in the Z basis
    measureB2 = QuantumCircuit(qr, cr, name='measureB2')
    measureB2.measure(qr[1], cr[1])

    # Measure Bob's qubit in the V basis
    measureB3 = QuantumCircuit(qr, cr, name='measureB3')
    measureB3.s(qr[1])
    measureB3.h(qr[1])
    measureB3.tdg(qr[1])
    measureB3.h(qr[1])
    measureB3.measure(qr[1], cr[1])

        # measurement of the spin projection of Alice's qubit onto the a_2 direction (W basis)
    measureEA2 = QuantumCircuit(qr, cr, name='measureEA2')
    measureEA2.s(qr[0])
    measureEA2.h(qr[0])
    measureEA2.t(qr[0])
    measureEA2.h(qr[0])
    measureEA2.measure(qr[0],cr[2])

    # measurement of the spin projection of Allice's qubit onto the a_3 direction (standard Z basis)
    measureEA3 = QuantumCircuit(qr, cr, name='measureEA3')
    measureEA3.measure(qr[0],cr[2])

    # measurement of the spin projection of Bob's qubit onto the b_1 direction (W basis)
    measureEB1 = QuantumCircuit(qr, cr, name='measureEB1')
    measureEB1.s(qr[1])
    measureEB1.h(qr[1])
    measureEB1.t(qr[1])
    measureEB1.h(qr[1])
    measureEB1.measure(qr[1],cr[3])

    # measurement of the spin projection of Bob's qubit onto the b_2 direction (standard Z measurement)
    measureEB2 = QuantumCircuit(qr, cr, name='measureEB2')
    measureEB2.measure(qr[1],cr[3])

    # lists of measurement circuits
    eveMeasurements = [measureEA2, measureEA3, measureEB1, measureEB2]
    ## Create measurement lists
    aliceMeasurements = [measureA1, measureA2, measureA3]
    bobMeasurements = [measureB1, measureB2, measureB3]

    # Define the number of singlets N
    numberOfSinglets = 500
    aliceMeasurementChoices = [random.randint(1, 3) for i in range(numberOfSinglets)]
    bobMeasurementChoices = [random.randint(1, 3) for i in range(numberOfSinglets)]
    # list of Eve's measurement choices
    # the first and the second elements of each row represent the measurement of Alice's and Bob's qubits by Eve respectively
    eveMeasurementChoices = []

    for j in range(numberOfSinglets):      
        if random.uniform(0, 1) <= 0.5: # in 50% of cases perform the WW measurement
            eveMeasurementChoices.append([0, 2])
        else: # in 50% of cases perform the ZZ measurement
            eveMeasurementChoices.append([1, 3])
    circuits = []  # List to store circuits

    for i in range(numberOfSinglets):
        # Create the circuit name based on Alice's and Bob's measurement choices
        circuitName = f"{i}:A{aliceMeasurementChoices[i]}_B{bobMeasurementChoices[i]}_E{eveMeasurementChoices[i][0]}_E{eveMeasurementChoices[i][1]}"
        
        # Create the joint measurement circuit
        # Add Alice's and Bob's measurement circuits to the singlet state circuit
        singlet_copy = singlet.copy()  # Create a copy of the singlet circuit to modify
        
        # Use compose() to combine circuits
        singlet_copy = singlet_copy.compose(eveMeasurements[eveMeasurementChoices[i][0] -1])
        singlet_copy = singlet_copy.compose(eveMeasurements[eveMeasurementChoices[i][1] -1 ])
        singlet_copy = singlet_copy.compose(aliceMeasurements[aliceMeasurementChoices[i] - 1])
        singlet_copy = singlet_copy.compose(bobMeasurements[bobMeasurementChoices[i] - 1])
       
        
        singlet_copy.name = circuitName
        
        # Add the created circuit to the circuits list
        circuits.append(singlet_copy)

    
    backend = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(circuits, backend)
    job = backend.run(compiled_circuit, shots=1)
    result = job.result()
    # Obtenemos el diccionario de resultados de medición

   

  


    #print(result) # uncomment for detailed result

    print(circuits[0].name)
    print (circuits[0].draw())
    print(result.get_counts(circuits[0]))

    print(circuits[1].name)
    print (circuits[1].draw())
    print(result.get_counts(circuits[1]))

    print(circuits[2].name)
    print (circuits[2].draw())
    print(result.get_counts(circuits[2]))

    print(circuits[3].name)
    print (circuits[3].draw())
    print(result.get_counts(circuits[3]))

    print(circuits[4].name)
    print (circuits[4].draw())
    print(result.get_counts(circuits[4]))
    
    
    

    # print(plot_histogram(counts))

    # plot_histogram(counts)
 
    abPatterns = [
    re.compile('..00$'), # search for the '..00' output (Alice obtained -1 and Bob obtained -1)
    re.compile('..01$'), # search for the '..01' output
    re.compile('..10$'), # search for the '..10' output (Alice obtained -1 and Bob obtained 1)
    re.compile('..11$')  # search for the '..11' output
    ]
    aliceResults = [] # Alice's results (string a)
    bobResults = [] # Bob's results (string a')
    ePatterns = [
        re.compile('00..$'), # search for the '00..' result (Eve obtained the results -1 and -1 for Alice's and Bob's qubits)
        re.compile('01..$'), # search for the '01..' result (Eve obtained the results 1 and -1 for Alice's and Bob's qubits)
        re.compile('10..$'),
        re.compile('11..$')  
    ]
# list of Eve's measurement results
# the elements in the 1-st column are the results obtaned from the measurements of Alice's qubits
# the elements in the 2-nd column are the results obtaned from the measurements of Bob's qubits
    eveResults = [] 

    # recording the measurement results
    for j in range(numberOfSinglets):
        
        res = list(result.get_counts(circuits[j]).keys())[0] # extract a key from the dict and transform it to str
        
        # Alice and Bob
        if abPatterns[0].search(res): # check if the key is '..00' (if the measurement results are -1,-1)
            aliceResults.append(-1) # Alice got the result -1 
            bobResults.append(-1) # Bob got the result -1
        if abPatterns[1].search(res):
            aliceResults.append(1)
            bobResults.append(-1)
        if abPatterns[2].search(res): # check if the key is '..10' (if the measurement results are -1,1)
            aliceResults.append(-1) # Alice got the result -1 
            bobResults.append(1) # Bob got the result 1
        if abPatterns[3].search(res): 
            aliceResults.append(1)
            bobResults.append(1)

        # Eve
        if ePatterns[0].search(res): # check if the key is '00..'
            eveResults.append([-1, -1]) # results of the measurement of Alice's and Bob's qubits are -1,-1
        if ePatterns[1].search(res):
            eveResults.append([1, -1])
        if ePatterns[2].search(res):
            eveResults.append([-1, 1])
        if ePatterns[3].search(res):
            eveResults.append([1, 1])
    aliceKey = [] # Alice's key string k
    bobKey = [] # Bob's key string k'
    eveKeys = [] # Eve's keys; the 1-st column is the key of Alice, and the 2-nd is the key of Bob

    # comparing the strings with measurement choices (b and b')
    for j in range(numberOfSinglets):
        # if Alice and Bob measured the spin projections onto the a_2/b_1 or a_3/b_2 directions
        if (aliceMeasurementChoices[j] == 2 and bobMeasurementChoices[j] == 1) or (aliceMeasurementChoices[j] == 3 and bobMeasurementChoices[j] == 2):  
            aliceKey.append(aliceResults[j]) # record the i-th result obtained by Alice as the bit of the secret key k
            bobKey.append(-bobResults[j]) # record the multiplied by -1 i-th result obtained Bob as the bit of the secret key k'
            eveKeys.append([eveResults[j][0], -eveResults[j][1]]) # record the i-th bits of the keys of Eve 

    keyLength = len(aliceKey) # length of the secret skey
    abKeyMismatches = 0 # number of mismatching bits in the keys of Alice and Bob
    eaKeyMismatches = 0 # number of mismatching bits in the keys of Eve and Alice
    ebKeyMismatches = 0 # number of mismatching bits in the keys of Eve and Bob

    for j in range(keyLength):
        if aliceKey[j] != bobKey[j]: 
            abKeyMismatches += 1
        if eveKeys[j][0] != aliceKey[j]:
            eaKeyMismatches += 1
        if eveKeys[j][1] != bobKey[j]:
            ebKeyMismatches += 1
    eaKnowledge = (keyLength - eaKeyMismatches)/keyLength # Eve's knowledge of Bob's key
    ebKnowledge = (keyLength - ebKeyMismatches)/keyLength # Eve's knowledge of Alice's key
    
    
    
    
    
    def chsh_corr(result):
        
        # lists with the counts of measurement results
        # each element represents the number of (-1,-1), (-1,1), (1,-1) and (1,1) results respectively
        countA1B1 = [0, 0, 0, 0] # XW observable
        countA1B3 = [0, 0, 0, 0] # XV observable
        countA3B1 = [0, 0, 0, 0] # ZW observable
        countA3B3 = [0, 0, 0, 0] # ZV observable

        for i in range(numberOfSinglets):

            res = list(result.get_counts(circuits[i]).keys())[0]

            # if the spins of the qubits of the i-th singlet were projected onto the a_1/b_1 directions
            if (aliceMeasurementChoices[i] == 1 and bobMeasurementChoices[i] == 1):
                for j in range(4):
                    if abPatterns[j].search(res):
                        countA1B1[j] += 1

            if (aliceMeasurementChoices[i] == 1 and bobMeasurementChoices[i] == 3):
                for j in range(4):
                    if abPatterns[j].search(res):
                        countA1B3[j] += 1

            if (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 1):
                for j in range(4):
                    if abPatterns[j].search(res):
                        countA3B1[j] += 1
                        
            # if the spins of the qubits of the i-th singlet were projected onto the a_3/b_3 directions
            if (aliceMeasurementChoices[i] == 3 and bobMeasurementChoices[i] == 3):
                for j in range(4):
                    if abPatterns[j].search(res):
                        countA3B3[j] += 1
                        
        # number of the results obtained from the measurements in a particular basis
        total11 = sum(countA1B1)
        total13 = sum(countA1B3)
        total31 = sum(countA3B1)
        total33 = sum(countA3B3)      
                        
        # expectation values of XW, XV, ZW and ZV observables (2)
        expect11 = (countA1B1[0] - countA1B1[1] - countA1B1[2] + countA1B1[3])/total11 # -1/sqrt(2)
        expect13 = (countA1B3[0] - countA1B3[1] - countA1B3[2] + countA1B3[3])/total13 # 1/sqrt(2)
        expect31 = (countA3B1[0] - countA3B1[1] - countA3B1[2] + countA3B1[3])/total31 # -1/sqrt(2)
        expect33 = (countA3B3[0] - countA3B3[1] - countA3B3[2] + countA3B3[3])/total33 # -1/sqrt(2) 
        
        corr = expect11 - expect13 + expect31 + expect33 # calculate the CHSC correlation value (3)
        
        return corr




    corr = chsh_corr(result) # CHSH correlation value

    # CHSH inequality test
    print('CHSH correlation value: ' + str(round(corr, 3)) + '\n')

    # Keys
    print('Length of the key: ' + str(keyLength))
    print('Number of mismatching bits: ' + str(abKeyMismatches) + '\n')

    print('Eve\'s knowledge of Alice\'s key: ' + str(round(eaKnowledge * 100, 2)) + ' %')
    print('Eve\'s knowledge of Bob\'s key: ' + str(round(ebKnowledge * 100, 2)) + ' %')
    

start_sender()