import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
    }
]


COINAPI_URL = 'https://rest.coinapi.io/v1'
COINAPI_KEY = 'D739D6DB-F7E8-4CDC-AF3B-5FD0F802D345'