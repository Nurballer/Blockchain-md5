import random
import math

# Check if a number is prime
def is_prime(number):
    if number < 2:
        return False
    for i in range(2, number // 2 + 1):
        if number % i == 0:
            return False
    return True

# Generate a random prime number within a range
def generate_prime(min_value, max_value):
    prime = random.randint(min_value, max_value)
    while not is_prime(prime):
        prime = random.randint(min_value, max_value)
    return prime

# Calculate modular inverse
def mod_inverse(e, phi):
    for d in range(3, phi):
        if (d * e) % phi == 1:
            return d
    raise ValueError("mod_inverse does not exist")

# Generate two distinct prime numbers
p, q = generate_prime(1000, 5000), generate_prime(1000, 5000)
while p == q:
    q = generate_prime(1000, 5000)

# Calculate n and phi_n
n = p * q
phi_n = (p - 1) * (q - 1)

# Generate public key 'e'
e = random.randint(3, phi_n - 1)
while math.gcd(e, phi_n) != 1:
    e = random.randint(3, phi_n - 1)

# Calculate private key 'd'
d = mod_inverse(e, phi_n)

# Print keys and values
print("Public Key: ", e)
print("Private Key: ", d)
print("n: ", n)
print("Phi of n: ", phi_n)
print("p", p)
print("q", q)

# Digital Signature Mechanism (Blyat RSA)
def sign(private_key, document):
    d, n = private_key
    # Convert the document to an integer (ensure the same format for signing and verification)
    document_int = int.from_bytes(document.encode('utf-8'), 'big')
    return pow(document_int, d, n)

def verify(public_key, document, signature):
    e, n = public_key
    # Convert the document to an integer (ensure the same format for signing and verification)
    document_int = int.from_bytes(document.encode('utf-8'), 'big')
    return pow(signature, e, n) == document_int

# Transaction verification
def verify_transaction(public_key, transaction, signature):
    try:
        document = f"{transaction['sender']}->{transaction['receiver']}:{transaction['amount']}"
        print(f"Verifying Document: {document}")
        if not verify(public_key, document, signature):
            raise ValueError("Signature is wrong")
    except Exception as e:
        raise ValueError(f"Document is wrong: {str(e)}")

# Blockchain Enhancements
class Block:
    def __init__(self, previous_hash, transactions, index):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hash(f"{self.index}{self.previous_hash}{self.transactions}")

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block("0", [], 0)

    def add_block(self, transactions):
        previous_block = self.chain[-1]
        new_block = Block(previous_block.hash, transactions, len(self.chain))
        self.chain.append(new_block)

# Example wallet
class Wallet:
    def __init__(self, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key

    def create_transaction(self, receiver, amount):
        transaction = {"sender": self.public_key, "receiver": receiver, "amount": amount}
        signature = sign(self.private_key, f"{self.public_key}->{receiver}:{amount}")
        return transaction, signature

# Example usage
blockchain = Blockchain()
wallet = Wallet((d, n), (e, n))

transactions = []
receiver_public_key = (e, n)
transaction, signature = wallet.create_transaction(receiver_public_key, 50)
transactions.append((transaction, signature))

for tx, sig in transactions:
    verify_transaction(receiver_public_key, tx, sig)
    blockchain.add_block([tx])

for block in blockchain.chain:
    print(f"Block {block.index}: {block.hash}")
    for tx in block.transactions:
        print(f"  {tx}")
