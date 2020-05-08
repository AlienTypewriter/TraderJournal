from .settings import COINAPI_KEY, COINAPI_URL
import requests

'''Various convenience methods for working with the API'''

def get_from_api(query):
        url = COINAPI_URL+query
        headers = {'X-CoinAPI-Key' : COINAPI_KEY}
        response = requests.get(url, headers=headers)
        return response.json()

def get_exchange_names():
        return [exch.get('name') for exch in get_from_api('/exchange')]