import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# functions.py
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def encrypt_message(message, key):
    """Encrypts a message with AES using a given key."""
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    iv = cipher.iv
    return iv + ct_bytes

def decrypt_message(ciphertext, key):
    """Decrypts an AES-encrypted message using a given key."""
    iv = ciphertext[:16]  # Extract the IV
    ct = ciphertext[16:]  # Extract the ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

# functions.py
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def simulate_bb84(length=128):
    """Simulates the BB84 protocol to generate a 16-byte shared key."""
    # Generate random bits for Alice and Bob and their bases
    alice_bits = [random.randint(0, 1) for _ in range(length)]
    alice_bases = [random.randint(0, 1) for _ in range(length)]
    bob_bases = [random.randint(0, 1) for _ in range(length)]
    
    # Bob "measures" Alice's qubits in random bases
    shared_key_bits = [alice_bits[i] for i in range(length) if alice_bases[i] == bob_bases[i]]
    
    # Ensure we have enough bits; if too few, generate additional random bits
    while len(shared_key_bits) < 128:
        shared_key_bits.extend([random.randint(0, 1) for _ in range(128 - len(shared_key_bits))])
    
    # Convert bits to a 16-byte (128-bit) key
    shared_key_str = ''.join(map(str, shared_key_bits[:128]))  # Take exactly 128 bits
    shared_key_bytes = int(shared_key_str, 2).to_bytes(16, byteorder='big')  # Convert to 16-byte key

    print("Clave compartida generada por BB84:", shared_key_bytes.hex())
    return shared_key_bits

# Generate shared key
shared_key = simulate_bb84()

# Generate shared key
shared_key = simulate_bb84()
def generate_random_bits(length):
    """Genera una secuencia aleatoria de bits de longitud dada."""
    return [random.randint(0, 1) for _ in range(length)]

def generate_random_bases(length):
    """Genera bases aleatorias de 0 (base Z) y 1 (base X)."""
    return [random.randint(0, 1) for _ in range(length)]
