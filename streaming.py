import requests
import time
import pandas as pd

while True:
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    data = response.json()
    price = data['bpi']['USD']['rate_float']
    
    print(f"Current BTC price: ${price}")
    time.sleep(5)
