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
        "index": int(index),
        "previousHash": str(currentHash),
        "timestamp": time.time(),
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
def refresh():
        print("refresh")
        response = requests.get(url)    
        block = response.json()

        # get index, timestamp, data, and CURRENT hash
        index, timestamp, data, currentHash = getData(block)

        # did the hash change? if so, reset nonce
        if currentHash != previousHash:
            print("hash change: was ", previousHash, ", now ", currentHash, sep="")
            nonce = reset_nonce(10)
        
        return index, timestamp, data, currentHash

'''
main
'''
if __name__ == "__main__":
    url = LATEST_BLOCK
    difficulty = DIFFICULTY
    sleepTime = 0.1
    
    previousHash = "[BEGIN_PROGRAM]"
    currentHash = ""
    nonce = reset_nonce(10)
    prefix = '0' * difficulty

    counter = 0
    limit = 10**6
    response = requests.get(url)    
    block = response.json()

    # get index, timestamp, data, and CURRENT hash
    index, timestamp, data, currentHash = refresh()

    while True:        
        if counter > limit:
            index, timestamp, data, currentHash = refresh()
            counter = 0
        
        # try to generate a new hash:
        newHash = calculate_hash(index, currentHash, timestamp, data, nonce)            
        if newHash.startswith(prefix):
            print("Nonce found:", nonce)
            print("Block hash with 7 leading zeros:", newHash)
            submitBlock(index, currentHash, timestamp, nonce, newHash)     
        
        # increment nonce
        nonce += 1
        previousHash = currentHash
        counter += 1
        #time.sleep(sleepTime)
