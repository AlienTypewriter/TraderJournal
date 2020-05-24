from django.core.exceptions import ObjectDoesNotExist
import requests

from .settings import API_KEY,API_URL
from .models import Period
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
        query = f'/symbols?filter_symbol_id={currency_id}'
        if not get_from_api(query):
                return False
        else:
                return True

def get_current_period():
        try:
                current_period=Period.objects.get(date_end__gte=date.today(),date_start__lte=date.today())
                return current_period
        except ObjectDoesNotExist:
                return None