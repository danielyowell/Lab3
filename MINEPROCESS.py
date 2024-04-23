'''
necessary imports
'''
import requests
import hashlib
import json
import time
from random import randint

DIFFICULTY = 7
LATEST_BLOCK = 'https://miners.sooners.us/latest_block.php'
SUBMIT_BLOCK = 'https://miners.sooners.us/submit_block.php'
MY_DATA = "Daniel Yowell"
_index = 0
_timestamp = ""
_data = ""
_previousHash = "[BEGIN_PROGRAM]"
_currentHash = ""
_nonce = 0
prefix = '0' * DIFFICULTY
_block_header = ""

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
    block_header = str(index) + str(previous_hash) + str(timestamp) + str(MY_DATA) + str(nonce)
    global _block_header
    _block_header = block_header
    #print(hashlib.sha256(block_header.encode()).hexdigest())
    return hashlib.sha256(block_header.encode()).hexdigest()

'''
congratulations! your hash met the difficulty requirement.
now pack it up and submit
'''
def submitBlock(index, currentHash, timestamp, nonce, newHash):
    file = open("myblocks.txt", "a")
    payload = {
        "index": int(index),
        "previousHash": str(currentHash),
        "timestamp": timestamp,
        "data": "Daniel Yowell",
        "nonce": int(nonce),
        "hash": str(newHash)
    }

    print("===HEADER===")
    global _block_header
    print(_block_header)

    print("===PAYLOAD===")
    print(payload)
    file.write("===PAYLOAD===\n")
    file.write(str(payload))
    file.write("\n")

    # convert to JSON
    payload_json = json.dumps(payload)

    # set Content-Type header (prevents url encoding)
    headers = {'Content-Type': 'application/json'}

    response = requests.post(SUBMIT_BLOCK, data=payload_json, headers=headers)
    print("===RESULTS===")
    print("STATUS:  ", json.loads(response.text)["status"])
    print("MESSAGE: ", json.loads(response.text)["message"])
    
    a = "STATUS:  " + str(json.loads(response.text)["status"]) + "\n"
    b = "MESSAGE: " + str(json.loads(response.text)["message"]) + "\n"
    file.write(a)
    file.write(b)
    file.write("===+++++++===\n")

'''
retrives info from latest block
'''
def getData(block): # block["data"]["timestamp"] , block["data"]["data"]
    return block["data"]["index"], block["data"]["hash"]

def refresh():
    print("refresh")
    response = requests.get(LATEST_BLOCK)    
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        return

    block = response.json()
    # get index and CURRENT hash
    _index, _currentHash = getData(block)

    global _previousHash
    global _nonce
    # did the hash change? if so, reset nonce
    if _currentHash != _previousHash:
        print("hash change: was ", _previousHash, ", now ", _currentHash, sep="")
        _nonce = random_with_N_digits(10)
        _previousHash = _currentHash
    
    # increment index
    _index += 1 

    return _index, _currentHash, _nonce

'''
main
'''
def main():
    # get the current index, timestamp, and hash
    _index, _currentHash, _nonce = refresh() 
          
    # try to generate a new hash:
    while True:
        TIMESTAMP = int(time.time())
        newHash = calculate_hash(_index, _currentHash, TIMESTAMP, MY_DATA, _nonce)            
        if newHash.startswith(prefix):
            file = open("myblocks.txt", "a")
            file.write("===+++++++===\n")
            a = "NEW POTENTIAL BLOCK" + "\n"
            b = "Index: " + str(_index) + "\n"
            c = "Previous hash: " + str(_currentHash) + "\n"
            d = "Timestamp: " + str(TIMESTAMP) + "\n"
            e = "Data: " + MY_DATA + "\n"
            f = "Nonce: " + str(_nonce) + "\n"
            g = "Full string: " + str(_index) + str(_currentHash) + str(TIMESTAMP) + MY_DATA + str(_nonce) + "\n"
            h = "New hash: " + str(newHash) + "\n"
            file.write(a)
            file.write(b)
            file.write(c)
            file.write(d)
            file.write(e)
            file.write(f)
            file.write(g)
            file.write(h)
            file.close()
            print(a,b,c,d,e,f,g,h)
            submitBlock(_index, _currentHash, TIMESTAMP, _nonce, newHash)
            _index, _currentHash, _nonce = refresh() 
        # increment nonce
        _nonce += 1
        if _nonce % 1000000 == 0:
            _index, _currentHash, _nonce = refresh()

if __name__ == "__main__":
    main()