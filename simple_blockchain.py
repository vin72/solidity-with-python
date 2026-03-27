# =============================================================================
# SIMPLE BLOCKCHAIN IN PYTHON
# A beginner-friendly example showing how a blockchain works from scratch.
#
# HOW TO RUN:
#   1. Make sure Python 3 is installed (https://python.org)
#   2. Open a terminal in this folder
#   3. Run:  python simple_blockchain.py
#
# NO extra libraries needed — only Python's built-in tools are used.
# =============================================================================

import hashlib   # Built-in tool for creating "fingerprints" (hashes) of data
import json      # Built-in tool for turning Python objects into readable text
import time      # Built-in tool for getting the current time


# =============================================================================
# GLOSSARY — Key blockchain words explained in plain English
# =============================================================================
#
#  BLOCK      — A container that holds a group of data (like a page in a book).
#               Each block stores: its own data, a timestamp, and a link to the
#               block before it.
#
#  HASH       — A unique "fingerprint" of data. Change even one letter and the
#               fingerprint changes completely. Think of it like a seal on an
#               envelope — if the seal is broken, you know something changed.
#
#  CHAIN      — Blocks are linked together using hashes. Each block stores the
#               hash of the block before it. This creates a chain. If someone
#               edits an old block, its hash changes, which breaks every block
#               after it — making tampering obvious.
#
#  GENESIS BLOCK — The very first block. It has no "previous block", so its
#               previous hash is just set to "0".
#
#  NONCE      — A number miners keep changing until the block's hash meets a
#               certain rule (e.g. starts with "0000"). This is "Proof of Work".
#
#  MINING     — The process of finding the right nonce so the hash passes the
#               difficulty rule. It takes effort (computing power), which is
#               why adding fake blocks to a chain is hard.
#
#  DIFFICULTY — How hard mining is. A difficulty of 3 means the hash must start
#               with "000". Higher difficulty = more guesses needed.
#
#  PROOF OF WORK — A way to prove that real computing effort was spent creating
#               a block. This makes cheating expensive.
#
#  VALIDITY   — A chain is valid only if: every block's hash is correct AND
#               every block correctly points to the one before it.
# =============================================================================


# =============================================================================
# STEP 1 — Define what a single BLOCK looks like
# =============================================================================

class Block:
    """
    One block in the blockchain.
    Think of it as one page in a ledger book.
    """

    def __init__(self, index, data, previous_hash):
        """
        Called automatically when you create a new block.

        Parameters:
            index         — The block's position in the chain (0, 1, 2, ...)
            data          — Whatever you want to store (e.g. a transaction)
            previous_hash — The fingerprint (hash) of the block before this one
        """
        self.index         = index          # Position in the chain
        self.timestamp     = time.time()    # When this block was created (seconds since 1970)
        self.data          = data           # The actual content being stored
        self.previous_hash = previous_hash  # Links this block to the one before it
        self.nonce         = 0              # Starts at 0; will be changed during mining
        self.hash          = self.calculate_hash()  # This block's own fingerprint

    def calculate_hash(self):
        """
        Creates a unique fingerprint for this block.

        We turn all the block's contents into one big string, then run it
        through SHA-256 (a standard hashing algorithm) to get a fixed-length
        fingerprint. Even a tiny change in the data will produce a completely
        different fingerprint.
        """
        # Combine everything important into one string
        block_string = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce
        }, sort_keys=True)  # sort_keys keeps the order consistent

        # Run it through SHA-256 and return the result as a hex string
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty):
        """
        MINING: Keep changing the nonce until the hash starts with enough zeros.

        Why zeros? It's just a rule the network agrees on. Finding a hash that
        starts with "000" requires many attempts — that's the "work" in
        Proof of Work.

        Parameters:
            difficulty — How many leading zeros the hash must have
        """
        target = "0" * difficulty  # e.g. difficulty=3 → target = "000"

        # Keep trying different nonces until the hash starts with enough zeros
        while not self.hash.startswith(target):
            self.nonce += 1              # Try the next number
            self.hash = self.calculate_hash()  # Recalculate the hash

        print(f"  Block {self.index} mined! Nonce: {self.nonce} | Hash: {self.hash[:20]}...")


# =============================================================================
# STEP 2 — Define the BLOCKCHAIN (a sequence of linked blocks)
# =============================================================================

class Blockchain:
    """
    The full chain of blocks.
    Manages adding new blocks and checking whether the chain has been tampered with.
    """

    def __init__(self, difficulty=3):
        """
        Creates a new blockchain and automatically adds the Genesis Block.

        Parameters:
            difficulty — How hard mining should be (default: 3 leading zeros)
        """
        self.difficulty = difficulty   # Mining difficulty setting
        self.chain = []                # Start with an empty list of blocks

        # Every blockchain starts with a special first block called the Genesis Block
        self.chain.append(self._create_genesis_block())

    def _create_genesis_block(self):
        """
        Creates the Genesis Block — block #0, the very start of the chain.

        Since there is no block before it, previous_hash is set to "0".
        """
        print("Creating Genesis Block (block #0, the very first block)...")
        genesis = Block(index=0, data="Genesis Block", previous_hash="0")
        genesis.mine(self.difficulty)
        return genesis

    def get_last_block(self):
        """Returns the most recently added block."""
        return self.chain[-1]

    def add_block(self, data):
        """
        Creates a new block, links it to the chain, and mines it.

        Steps:
            1. Get the hash of the last block (this becomes our 'previous_hash')
            2. Create a new block with that link
            3. Mine the block (find a valid nonce)
            4. Append it to the chain
        """
        previous_hash = self.get_last_block().hash       # Grab the last block's fingerprint
        new_block = Block(
            index         = len(self.chain),             # Next position in the chain
            data          = data,                        # The content to store
            previous_hash = previous_hash               # Link to the previous block
        )
        new_block.mine(self.difficulty)                  # Do the "work"
        self.chain.append(new_block)                     # Add to the chain
        print(f"  Block {new_block.index} added to chain.\n")

    def is_valid(self):
        """
        Checks whether the entire blockchain is intact and untampered.

        Two checks for every block (except the Genesis Block):
            1. The block's stored hash still matches a fresh calculation
               (catches changes to the block's data)
            2. The block's previous_hash matches the actual hash of the prior block
               (catches broken links between blocks)

        Returns True if everything is fine, False if something was tampered with.
        """
        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            # Check 1: Has this block's data been altered?
            if current.hash != current.calculate_hash():
                print(f"  ALERT: Block {i} has been tampered with! Hash mismatch.")
                return False

            # Check 2: Is this block still correctly linked to the previous one?
            if current.previous_hash != previous.hash:
                print(f"  ALERT: Block {i} is broken from block {i-1}! Chain is broken.")
                return False

        return True  # All checks passed

    def display(self):
        """Prints a readable summary of every block in the chain."""
        print("\n" + "=" * 60)
        print("  BLOCKCHAIN CONTENTS")
        print("=" * 60)
        for block in self.chain:
            print(f"\n  Block #{block.index}")
            print(f"    Data          : {block.data}")
            print(f"    Nonce         : {block.nonce}")
            print(f"    Previous Hash : {block.previous_hash[:30]}...")
            print(f"    Hash          : {block.hash[:30]}...")
        print("\n" + "=" * 60)


# =============================================================================
# STEP 3 — Run a demo to see everything in action
# =============================================================================

if __name__ == "__main__":
    # --- Build the chain ---
    print("\n>>> Building a simple blockchain...\n")
    my_chain = Blockchain(difficulty=3)   # Hashes must start with "000"

    # Add some blocks — in a real system these would be financial transactions
    my_chain.add_block("Alice sends Bob 10 coins")
    my_chain.add_block("Bob sends Carol 5 coins")
    my_chain.add_block("Carol sends Dave 2 coins")

    # --- Display the chain ---
    my_chain.display()

    # --- Verify the chain ---
    print("\n>>> Checking if the chain is valid...")
    print("  Result:", "VALID — no tampering detected." if my_chain.is_valid() else "INVALID!")

    # --- Demonstrate tampering ---
    print("\n>>> Simulating tampering: changing Block 1's data...")
    my_chain.chain[1].data = "Alice sends Bob 1000 coins"  # Sneaky edit!
    # Note: we did NOT re-mine, so the hash no longer matches the data

    print("\n>>> Checking chain validity after tampering...")
    print("  Result:", "VALID" if my_chain.is_valid() else "INVALID — tampering detected!")

    # --- Key takeaway ---
    print("""
===========================================================
  KEY TAKEAWAY
===========================================================
  When we edited Block 1's data without re-mining, its hash
  no longer matched — the chain immediately flagged it as
  invalid. This is why blockchains are tamper-evident: you
  cannot secretly change old data without breaking every
  block that comes after it, and you'd need enormous
  computing power to re-mine them all.
===========================================================
""")
