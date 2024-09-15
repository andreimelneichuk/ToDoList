import jwt

token = 'YOUR_JWT_TOKEN'
secret_key = 'django-insecure-dev-key-replace-me'

try:
    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    print("Токен действителен:", payload)
except jwt.ExpiredSignatureError:
    print("Токен истек")
except jwt.InvalidTokenError:
    print("Неверный токен")