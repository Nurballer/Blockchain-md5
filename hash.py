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
    X = [int.from_bytes(block[i:i+4], 'little') for i in range(0, 65, 4)]

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


def md5(self):
    global A, B, C, D
    A, B, C, D = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
    self = append_bits(list(self.encode('utf-8')))

    for i in range(0, len(self), 64):
        process_block(self[i:i+64])

    return ''.join(f'{x:02x}' for x in sum([(v << (32 * i)) for i, v in enumerate([A, B, C, D])], 0).to_bytes(16, 'little'))
    

def md5_hexdigest(data):
    final_hash = md5(data)  # Get the MD5 hash as bytes
    return ''.join(f'{byte:02x}' for byte in final_hash)  # Convert each byte to hexadecimal string


# Function to compute MD5 hash without external libraries
def md5(data):
    # Placeholder for the MD5 hashing function (user-defined above)
    return data  # Replace with actual MD5 function implementation

class MerkleTree:
    # Constructor to initialize Merkle Tree with transactions
    def __init__(self, transactions):
        self.transactions = transactions
        self.root = self.build_merkle_root()

    # Build the Merkle root by hashing pairs of transactions
    def build_merkle_root(self):
        nodes = [md5(tx) for tx in self.transactions]
        while len(nodes) > 1:
            if len(nodes) % 2 == 1:  # If odd, duplicate the last node
                nodes.append(nodes[-1])
            nodes = [md5(nodes[i] + nodes[i + 1]) for i in range(0, len(nodes), 2)]
        return str(nodes[0]) if nodes else ''

class Block:
    # Constructor for the Block class
    def __init__(self, transactions, prev_hash):
        self.timestamp = self.get_timestamp()
        self.prev_hash = prev_hash
        self.merkle_tree = MerkleTree(transactions)
        self.hash = self.mine_block()

    # Replace time with a manual timestamp
    def get_timestamp(self):
        return sum([ord(c) for c in md5(str(self))]) % 10000000000

    # Mine the block by finding a valid hash with a given difficulty
    def mine_block(self, difficulty=4):
        nonce = 0
        target = '0' * difficulty
        while True:
            hash_value = md5(str(self.timestamp) + self.prev_hash + self.merkle_tree.root + str(nonce))
            if hash_value[:difficulty] == target:
                return hash_value
            nonce += 1

class Blockchain:
    # Constructor for the Blockchain class
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    # Method to create the first block in the blockchain
    def create_genesis_block(self):
        transactions = ["Genesis Transaction"]
        return Block(transactions, "0")

    # Method to add a new block to the blockchain
    def add_block(self, transactions):
        prev_block = self.chain[-1]
        new_block = Block(transactions, prev_block.hash)
        self.chain.append(new_block)

    # Validate the blockchain
    def validate_blockchain(self):
        for i in range(1, len(self.chain)):
            curr_block = self.chain[i]
            prev_block = self.chain[i - 1]
            if curr_block.prev_hash != prev_block.hash:
                return False
            if curr_block.hash != curr_block.mine_block():
                return False
        return True

# Test the Blockchain
blockchain = Blockchain()

# Add blocks to the Blockchain with transactions
blockchain.add_block(["A->B:10", "C->D:20", "E->F:30"])
blockchain.add_block(["G->H:40", "I->J:50", "K->L:60"])
blockchain.add_block(["M->N:70", "O->P:80", "Q->R:90"])

# Print Blockchain
print('Blockchain:')
for block in blockchain.chain:
    print('Timestamp:', block.timestamp)
    print('Merkle Root:', block.merkle_tree.root)
    print('Previous hash:', block.prev_hash)
    print('Hash:', block.hash)
    print()

# Validate the blockchain
print('Is Blockchain valid?', blockchain.validate_blockchain())
