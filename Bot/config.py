API_TOKEN = '7278441677:AAE6o6B50DTEQkbvDmpFD7sHSJBO3k2jx2w'
DJANGO_API_URL = "http://django:8000/api/"
FASTAPI_URL = "http://fastapi:8001/comments/"

# Логин и пароль для получения токена
DJANGO_USERNAME = None
DJANGO_PASSWORD = None

def set_django_credentials(username, password):
    global DJANGO_USERNAME, DJANGO_PASSWORD
    DJANGO_USERNAME = username
    DJANGO_PASSWORD = password

def get_django_credentials():
    return DJANGO_USERNAME, DJANGO_PASSWORD

ACCESS_TOKEN = None
REFRESH_TOKEN = None

def set_django_tokens(ACCESS, REFRESH):
    global ACCESS_TOKEN, REFRESH_TOKEN
    ACCESS_TOKEN = ACCESS
    REFRESH_TOKEN = REFRESH

def get_django_tockens():
    return ACCESS_TOKEN, REFRESH_TOKEN