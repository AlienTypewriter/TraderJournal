from django.core.exceptions import ObjectDoesNotExist
import requests

from .settings import API_KEY,API_URL
from datetime import date

'''Various convenience methods for working with the API'''

def get_from_api(query):
        url = API_URL+query
        headers = {'X-CoinAPI-Key' : API_KEY}
        response = requests.get(url, headers=headers)
        return response.json()

def get_exchange_names():
        return [exch.get('name') for exch in get_from_api('/exchange')]

def check_currency(currency_id):
        query = f'/exchangerate/{currency_id}/USD'
        result = get_from_api(query)
        if result.get('error') is not None:
                return False
        else:
                return True