import requests
import json

def generateNewBlock():
    print("x")

def getData(data):
    print(data["status"])
    print(data["data"])
    print(data["data"]["hash"])

def main():
    url = 'https://miners.sooners.us/latest_block.php'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        getData(data)
    else:
        print(f"Request failed with status code {response.status_code}")

if __name__ == "__main__":
    main()