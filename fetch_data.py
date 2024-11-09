import requests

def fetch_crypto_data(timeframe='DAILY'):
    url = f'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_{timeframe}&symbol=BTC&market=EUR&apikey=demo'
    response = requests.get(url)
    return response.json()
