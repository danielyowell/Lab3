import asyncio
import aiohttp
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

async def mine_block(url, difficulty):
    previousHash = "[BEGIN_PROGRAM]"
    currentHash = ""
    nonce = random_with_N_digits(10)
    prefix = '0' * difficulty
    
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url) as response:
                if response.status == 200:
                    block = await response.json()
                    index, timestamp, data, currentHash = getData(block)
                    
                    if currentHash != previousHash:
                        print("hash change: was ", previousHash, ", now ", currentHash, sep="")
                    
                    newHash = calculate_hash(index, currentHash, timestamp, data, nonce)
                    if newHash.startswith(prefix):
                        print("Nonce found:", nonce)
                        print("Block hash with 7 leading zeros:", newHash)
                        await submit_block(session, index, currentHash, timestamp, nonce, newHash)
                    
                    nonce = random_with_N_digits(10)
                else:
                    print(f"Request failed with status code {response.status}")
            previousHash = currentHash

async def submit_block(session, index, currentHash, timestamp, nonce, newHash):
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
    
    headers = {'Content-Type': 'application/json'}
    async with session.post('https://miners.sooners.us/submit_block.php', json=payload, headers=headers) as response:
        data = await response.json()
        print("===RESULTS===")
        print("STATUS:  ", data["status"])
        print("MESSAGE: ", data["message"])

if __name__ == "__main__":
    url = 'https://miners.sooners.us/latest_block.php'
    difficulty = 7

    asyncio.run(mine_block(url, difficulty))
