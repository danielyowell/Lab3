import threading

'''
necessary imports
'''
import requests
import hashlib
import json
import time
from random import randint

# 'https://submit_block.php'
# 'https://miners.sooners.us/submit_block.php' 
SUBMIT_BLOCK = 'https://miners.sooners.us/submit_block.php'

# 'latest_block.php'
# 'https://miners.sooners.us/latest_block.php'
LATEST_BLOCK = 'https://miners.sooners.us/latest_block.php'

DIFFICULTY = 7

'''
generate random 10 digit number
'''
def reset_nonce(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

"""
calculate the hash value of a block
"""
def calculate_hash(index, previous_hash, timestamp, data, nonce):
    block_header = str(index) + previous_hash + str(timestamp) + data + str(nonce)
    return hashlib.sha256(block_header.encode()).hexdigest()

'''
congratulations! your hash met the difficulty requirement.
now pack it up and submit
'''
def submitBlock(index, currentHash, timestamp, nonce, newHash):
    payload = {
        "index": int(index + 1),
        "previousHash": str(currentHash),
        "timestamp": int(time.time()),
        "data": "Daniel Yowell",
        "nonce": int(nonce),
        "hash": str(newHash)
    }

    print("===PAYLOAD===")
    print(payload)

    # convert to JSON
    payload_json = json.dumps(payload)

    # set Content-Type header (prevents url encoding)
    headers = {'Content-Type': 'application/json'}

    response = requests.post(SUBMIT_BLOCK, data=payload_json, headers=headers)
    print("===RESULTS===")
    print("STATUS:  ", json.loads(response.text)["status"])
    print("MESSAGE: ", json.loads(response.text)["message"])

'''
retrives info from latest block
'''
def getData(block):
    return block["data"]["index"], block["data"]["timestamp"], block["data"]["data"], block["data"]["hash"]

'''
refresh
'''
def refresh(currentHash):
        print("refresh")
        response = requests.get(url)    
        block = response.json()

        # get index, timestamp, data, and CURRENT hash
        index, timestamp, data, newHash = getData(block)

        # did the hash change? if so, reset nonce
        if newHash != currentHash:
            print("hash change: was ", currentHash, ", now ", newHash, sep="")
            nonce = reset_nonce(10)
        
        return index, timestamp, data, currentHash

class MinerThread(threading.Thread):
    def __init__(self, index, timestamp, data, currentHash, nonce, prefix, limit):
        super().__init__()
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.currentHash = currentHash
        self.nonce = nonce
        self.prefix = prefix
        self.limit = limit
        self.new_hash = None

    def run(self):
        response = requests.get(url)
        block = response.json()
        index, timestamp, data, currentHash = getData(block)
        while True:
            new_hash = calculate_hash(index, currentHash, timestamp, data, self.nonce)
            if new_hash.startswith(self.prefix):
                self.new_hash = new_hash
                break
            self.nonce += 1
            counter += 1

if __name__ == "__main__":
    url = LATEST_BLOCK
    difficulty = DIFFICULTY
    prefix = '0' * difficulty
    limit = 10**6

    response = requests.get(url)
    block = response.json()
    index, timestamp, data, currentHash = getData(block)
    nonce = reset_nonce(10)

    num_threads = 4  # Number of threads to create
    threads = []

    while True:
        # Create and start threads
        for i in range(num_threads):
            thread = MinerThread(index, timestamp, data, currentHash, reset_nonce(10), prefix, limit // num_threads)
            threads.append(thread)
            thread.start()

        # Wait for threads to complete
        for thread in threads:
            thread.join()

        # Check if any thread found a valid hash
        for thread in threads:
            if thread.new_hash:
                print("Nonce found:", thread.nonce)
                print("Block hash with", difficulty, "leading zeros:", thread.new_hash)
                submitBlock(index, currentHash, timestamp, thread.nonce, thread.new_hash)