from .settings import API_KEY,API_URL
import requests

'''Various convenience methods for working with the API'''

def get_from_api(query):
        url = API_URL+query
        headers = {'X-CoinAPI-Key' : API_KEY}
        response = requests.get(url, headers=headers)
        return response.json()

def get_exchange_names():
        return [exch.get('name') for exch in get_from_api('/exchange')]

def check_currency(currency_id):
        query = f'/symbols?filter_symbol_id={currency_id}'
        if not get_from_api(query):
                return False
        else:
                return True