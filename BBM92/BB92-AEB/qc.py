
import socket
import threading
import numpy as np
import pickle
import struct
import random
from qiskit import QuantumCircuit
from Crypto.Cipher import AES
from qiskit import transpile
from datetime import datetime
import hashlib
from qiskit_aer import AerSimulator
import numpy as np
import tkinter as tk
import os
from qiskit_aer import Aer
from qiskit import QuantumCircuit
SIZE = 1
      # Crear circuito cuántico con entrelazamiento
qc = QuantumCircuit(2, 2)  # 2 qubits, 2 bits clásicos
qc.h(0)  # Puerta Hadamard en qubit 0
qc.cx(0, 1)  # CNOT para entrelazar qubit 0 y 1
print("Circuito cuántico creado:\n", qc)

backend = Aer.get_backend('qasm_simulator')
compiled_circuit = transpile(qc, backend)
job = backend.run(compiled_circuit, shots=1)  # Ejecutar el circuito.
result = job.result()
