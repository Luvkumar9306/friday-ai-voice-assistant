import jwt, time

payload = {
    'iss': 'devkey',
    'sub': 'boss',
    'name': 'Boss',
    'exp': int(time.time()) + 86400,
    'nbf': int(time.time()),
    'jti': 'boss',
    'video': {
        'room': 'friday-room',
        'roomJoin': True,
        'canPublish': True,
        'canSubscribe': True,
        'canPublishData': True
    }
}

token = jwt.encode(payload, 'secret', algorithm='HS256')
print(token)
