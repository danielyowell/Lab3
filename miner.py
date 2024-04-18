'''
necessary imports
'''
import requests
import hashlib
import json
import time
from random import randint

'''
generate random 10 digit number
'''
def random_with_N_digits(n):
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

    response = requests.post('https://miners.sooners.us/submit_block.php', data=payload_json, headers=headers)
    print("===RESULTS===")
    print("STATUS:  ", json.loads(response.text)["status"])
    print("MESSAGE: ", json.loads(response.text)["message"])

'''
retrives info from latest block
'''
def getData(block):
    return block["data"]["index"], block["data"]["timestamp"], block["data"]["data"], block["data"]["hash"]

'''
main
'''
if __name__ == "__main__":
    #main()
    url = 'https://miners.sooners.us/latest_block.php'
    difficulty = 7

    previousHash = "[BEGIN_PROGRAM]"
    currentHash = ""
    nonce = random_with_N_digits(10)
    prefix = '0' * difficulty

    while True:
        response = requests.get(url)    
        if response.status_code == 200:
            block = response.json()
            # get index, timestamp, data, and CURRENT hash
            index, timestamp, data, currentHash = getData(block)
            
            # did the hash change? if so, reset nonce
            if currentHash != previousHash:
                print("hash change: was ", previousHash, ", now ", currentHash, sep="")
                #nonce = 0
            
            # try to generate a new hash:
            newHash = calculate_hash(index, currentHash, timestamp, data, nonce)            
            if newHash.startswith(prefix):
                print("Nonce found:", nonce)
                print("Block hash with 7 leading zeros:", newHash)
                submitBlock(index, currentHash, timestamp, nonce, newHash)     
            
            # increment nonce
            nonce = random_with_N_digits(10)
        else:
            print(f"Request failed with status code {response.status_code}")
        previousHash = currentHash
