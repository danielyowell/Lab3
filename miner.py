'''
necessary imports
'''
import requests
import hashlib
import json
import time

"""
calculate the hash value of a block
"""
def calculate_hash(index, previous_hash, timestamp, data, nonce):
    block_header = str(index) + previous_hash + str(timestamp) + data + str(nonce)
    return hashlib.sha256(block_header.encode()).hexdigest()

"""
mine a block.
"""
def mine_block(index, previous_hash, timestamp, data, difficulty):
    prefix = '0' * difficulty
    nonce = 0
    while True:
        block_hash = calculate_hash(index, previous_hash, timestamp, data, nonce)
        if block_hash.startswith(prefix):
            print("Nonce found:", nonce)
            print("Block hash with 7 leading zeros:", block_hash)
            return nonce, block_hash
        nonce += 1


"""
create a block and send it to the sooners php
"""
def generateNewBlock(index, currentHash, timestamp, data, difficulty):
    print("currentHash:", currentHash)
    print("(This will be the previousHash of the block we are mining)")
    nonce, block_hash = mine_block(index, currentHash, timestamp, data, difficulty)

    payload = {
        "index": int(index),
        "previousHash": str(currentHash),
        "timestamp": timestamp,
        "data": "Daniel Yowell",
        "nonce": int(nonce),
        "hash": str(block_hash)
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
def main():
    url = 'https://miners.sooners.us/latest_block.php'
    response = requests.get(url)

    if response.status_code == 200:
        block = response.json()
        # get index, timestamp, data, and CURRENT hash
        index, timestamp, data, currentHash = getData(block)
        difficulty = 7
        generateNewBlock(index, currentHash, timestamp, data, difficulty)
    else:
        print(f"Request failed with status code {response.status_code}")

if __name__ == "__main__":
    #main()
    url = 'https://miners.sooners.us/latest_block.php'
    
    previousHash = "[BEGIN_PROGRAM]"
    currentHash = ""
    
    while True:
        response = requests.get(url)    
        if response.status_code == 200:
            block = response.json()
            # get index, timestamp, data, and CURRENT hash
            index, timestamp, data, currentHash = getData(block)
            # try to generate a new hash:
            # generateHash() # 
            # if hash = 7zeroes: # check for 7 zeroes
            if currentHash != previousHash:
                print("hash change: was ", previousHash, ", now ", currentHash, sep="")
        else:
            print(f"Request failed with status code {response.status_code}")
        previousHash = currentHash
        # time.sleep(3)