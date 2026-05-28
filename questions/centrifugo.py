import time

import jwt
import requests
from django.conf import settings


def channel_for_question(question_id):
    return f'{settings.CENTRIFUGO_NAMESPACE}:question_{question_id}'


def generate_connection_token(user_id):
    payload = {
        'sub': str(user_id) if user_id else '',
        'exp': int(time.time()) + settings.CENTRIFUGO_TOKEN_TTL,
    }
    return jwt.encode(payload, settings.CENTRIFUGO_TOKEN_SECRET, algorithm='HS256')


def publish(channel, data):
    response = requests.post(
        f'{settings.CENTRIFUGO_API_URL}/api/publish',
        json={'channel': channel, 'data': data},
        headers={'X-API-Key': settings.CENTRIFUGO_API_KEY},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()
