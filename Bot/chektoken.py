import jwt

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI2NDAyMTY1LCJpYXQiOjE3MjYzOTg1NjUsImp0aSI6IjlmOGI2Mzc5NThjMTQ3YjdiYzQ5NDJiZTU3YWRmYmIyIiwidXNlcl9pZCI6M30.0hAZLnKNHrLmRROqsaTAGXV71sf5D49NhjYDSk2YZNQ'
secret_key = 'django-insecure-y*vw@j7qzvft=g7h+d$um=k&731m)78-hr@8=8(qo8765in&dp'

try:
    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    print("Токен действителен:", payload)
except jwt.ExpiredSignatureError:
    print("Токен истек")
except jwt.InvalidTokenError:
    print("Неверный токен")