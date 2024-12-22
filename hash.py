A = 0x67452301
B = 0xefcdab89
C = 0x98badcfe
D = 0x10325476

S = [7, 12, 17, 22] * 4 + [5, 9, 14, 20] * 4 + [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4
# [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
#  5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
#  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
#  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

T = [(int(4294967296 * abs(i ** 0.5 % 1))) for i in range(1, 65)] # 4294967296 = 2^32
# T = [0xd76aa478, 0xe8c7b756, 0x242070db, ..., 0x8f1bbcdc]

def rotate_left(value, shift):
    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


def to_bytes(n, length):
    return [(n >> (8 * i)) & 0xFF for i in range(length)] # Move to (N)byte (8bit = 1byte) and make a list of bites
     

def append_bits(data):
    length = len(data) * 8 # Calculates data in bites, 1 byte = 8 bit
    data.append(0x80) # Append 1 bit such 0x80 in in hexadecimal, this signalize a end of data
    while (len(data) * 8) % 512 != 448: # Zeros are added until then, data length is such len 64 bits less than a multiple of 512, equal to 448
        data.append(0x00) #Zeros append in hexdeclimal
    data.extend(to_bytes(length, 8)) # Add elements from length to data, this divide to 8 elements in list
    return data


def process_block(block):
    global A, B, C, D # make changing in this func
    a, b, c, d = A, B, C, D # make local versions of variables
    X = [int.from_bytes(block[i:i+4], 'little') for i in range(0, 64, 4)]

    def func(f, a, b, c, d, x, s, t):
        a = (a + f(b, c, d) + x + t) & 0xFFFFFFFF
        return (b + rotate_left(a, s)) & 0xFFFFFFFF

    F = lambda x, y, z: (x & y) | (~x & z)
    G = lambda x, y, z: (x & z) | (y & ~z)
    H = lambda x, y, z: x ^ y ^ z
    I = lambda x, y, z: y ^ (x | ~z)

    for i in range(64):
        if i < 16:
            a, b, c, d = func(F, a, b, c, d, X[i], S[i], T[i]), a, b, c
        elif i < 32:
            a, b, c, d = func(G, a, b, c, d, X[(5 * i + 1) % 16], S[i], T[i]), a, b, c
        elif i < 48:
            a, b, c, d = func(H, a, b, c, d, X[(3 * i + 5) % 16], S[i], T[i]), a, b, c
        else:
            a, b, c, d = func(I, a, b, c, d, X[(7 * i) % 16], S[i], T[i]), a, b, c

    A = (A + a) & 0xFFFFFFFF
    B = (B + b) & 0xFFFFFFFF
    C = (C + c) & 0xFFFFFFFF
    D = (D + d) & 0xFFFFFFFF

def md5(data):
    global A, B, C, D
    A, B, C, D = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
    data = append_bits(list(data.encode('utf-8')))

    for i in range(0, len(data), 64):
        process_block(data[i:i+64])

    return ''.join(f'{x:02x}' for x in sum([(v << (32 * i)) for i, v in enumerate([A, B, C, D])], 0).to_bytes(16, 'little'))

def create_merkle_root(transactions):
    # Create Merkle root from a list of transactions using MD5
    merkle_layer = [md5(tx) for tx in transactions]
    while len(merkle_layer) > 1:
        temp_layer = []
        for i in range(0, len(merkle_layer), 2):
            pair = merkle_layer[i] + (merkle_layer[i + 1] if i + 1 < len(merkle_layer) else merkle_layer[i])
            temp_layer.append(md5(pair))
        merkle_layer = temp_layer
    return merkle_layer[0]

# List of possible names for senders and receivers
names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack", "Kenny", "Liam", "Mona", "Nina", "Oscar"]

# Simple PRNG (Pseudo-Random Number Generator)
def simple_prng(seed):
    # A basic linear congruential generator (LCG) for pseudo-random numbers
    a = 1664525  # Multiplier
    c = 1013904223  # Increment
    m = 2**32  # Modulus
    seed = (a * seed + c) % m
    return seed

# Updated Block class to handle transactions
class Block:
    def __init__(self, previous_hash, transactions, index):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = self.generate_timestamp()
        self.transactions = transactions  # List of transactions (dictionaries)
        self.hash = self.calculate_hash()

    def generate_timestamp(self):
        return self.index  # Placeholder, replace with actual timestamp logic

    def calculate_hash(self):
        return md5(self.__str__())

    def __str__(self):
        return f"{self.index}{self.previous_hash}{self.timestamp}{self.transactions}"

# Modified Blockchain class to add blocks with transactions
class Blockchain:
    def __init__(self):
        # Initialize index here before creating genesis block
        self.index = 0  # Ensure the index starts at 0 for the genesis block
        self.chain = [self.create_genesis_block()]
        
    def create_genesis_block(self):
        # Genesis block with no transactions
        return Block("0", [], self.index)

    def add_block(self, transactions):
        previous_block = self.chain[-1]
        new_block = Block(previous_block.hash, transactions, self.index)
        self.chain.append(new_block)
        self.index += 1

    def create_transactions(self, n, seed):
        # Generate n transactions with random sender, receiver, and amount using custom PRNG
        transactions = []
        for _ in range(n):
            seed = simple_prng(seed)  # Generate new pseudo-random value
            sender = names[seed % len(names)]  # Select a random sender
            seed = simple_prng(seed)  # Update seed
            receiver = names[(seed % len(names))]  # Select a random receiver
            while receiver == sender:  # Ensure the receiver isn't the same as the sender
                seed = simple_prng(seed)  # Update seed to avoid same sender and receiver
                receiver = names[(seed % len(names))]
            seed = simple_prng(seed)  # Update seed for amount
            amount = (seed % 1000) + 1  # Random amount between 1 and 1000
            transaction = {"sender": sender, "receiver": receiver, "amount": amount}
            transactions.append(transaction)
        return transactions

# Usage
blockchain = Blockchain()

# Add blocks with 10 random transactions each, using an incrementing seed (using index as seed)
seed = 12345678  # Initial arbitrary seed value
for _ in range(3):  # Add 3 blocks, each with 10 random transactions
    transactions = blockchain.create_transactions(10, seed)
    blockchain.add_block(transactions)

# Print block details
for block in blockchain.chain:
    print(f"Block {block.index}: {block.hash}")
    for tx in block.transactions:
        print(f"  Sender: {tx['sender']}, Receiver: {tx['receiver']}, Amount: {tx['amount']}")
