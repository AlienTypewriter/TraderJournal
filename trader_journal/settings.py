import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
    }
]


API_URL = 'https://rest.coinapi.io/v1'
API_KEY = '72E9C73A-ADF4-431E-9785-1190495AA9E6'