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
SUBMIT_BLOCK = 'http://localhost/MyWebsite/submit_block.php'

# 'latest_block.php'
# 'https://miners.sooners.us/latest_block.php'
LATEST_BLOCK = 'https://miners.sooners.us/latest_block.php'
DIFFICULTY = 6

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
    # print("STATUS:  ", json.loads(response.text)["status"])
    # print("MESSAGE: ", json.loads(response.text)["message"])

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
    diff = DIFFICULTY
    sleepTime = 0.1
    
    previousHash = "[BEGIN_PROGRAM]"
    currentHash = ""
    nonce = random_with_N_digits(10)
    prefix = '0' * diff

    response = requests.get(LATEST_BLOCK)    
    if response.status_code == 200:
        block = response.json()
        # get index, timestamp, data, and CURRENT hash
        index, timestamp, data, currentHash = getData(block)
        
        print("current hash:", currentHash)

        # try to generate a new hash:
        while True:
            newHash = calculate_hash(index, currentHash, timestamp, data, nonce)            
            if newHash.startswith(prefix):
                print("Nonce found:", nonce)
                print("Block hash with 7 leading zeros:", newHash)
                submitBlock(index, currentHash, timestamp, nonce, newHash)
                response = requests.get(LATEST_BLOCK) 
                block = response.json()
                # get index, timestamp, data, and CURRENT hash
                index, timestamp, data, currentHash = getData(block)
            # increment nonce
            nonce += 1     

    else:
        print(f"Request failed with status code {response.status_code}")
    previousHash = currentHash
