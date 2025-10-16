from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that retrieves the access token from browser cookies
    instead of requiring it in the Authorization header.
    """
        
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None  # no Token => not authenticated
        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid token")
