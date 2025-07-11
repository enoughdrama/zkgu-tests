import secrets
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .models import APIToken

class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        try:
            api_token = APIToken.objects.get(token=token, is_active=True)
            return (api_token.user, api_token)
        except APIToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

def generate_api_token(user):
    token = secrets.token_hex(32)
    api_token, created = APIToken.objects.get_or_create(
        user=user,
        defaults={'token': token}
    )
    if not created:
        api_token.token = token
        api_token.save()
    return api_token.token