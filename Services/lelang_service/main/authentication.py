import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth.models import AnonymousUser


class JWTUser:
    def __init__(self, payload):
        self.payload = payload
        self.is_authenticated = True

    @property
    def id(self):
        return self.payload.get("user_id")  # Assuming 'sub' is the user ID in your JWT

    @property
    def role(self):
        return self.payload.get("user_role")  # Assuming 'role' is present in the JWT payload

    # Optionally add any other properties you want to expose


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None

        if token.startswith('Bearer '):
            token = token[7:]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user = JWTUser(payload)  # Wrap the payload in the JWTUser object
        return (user, None)  # Return user object instead of raw payload
