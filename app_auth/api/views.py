import os
import django_rq
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .utils import send_user_email, send_welcome_email

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication

from dotenv import load_dotenv
load_dotenv()

User = get_user_model()

from .serializers import RegisterSerializer, RequestPasswordResetSerializer, ConfirmPasswordSerializer, LoginSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5500')
            activation_link = f"{frontend_url}/api/activate/{uid}/{token}/"

            django_rq.get_queue('default').enqueue(
                send_user_email,
                user,
                subject="Confirm your account",
                template_name="confirm_account",
                link_name="activation_link",
                link_value=activation_link
            )

            return Response(
                {"user": {"id": user.pk, "email": user.email}, "token": token},
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response(
                {"message": "Invalid or expired link."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.is_active:
            return Response(
                {"message": "Account already activated."},
                status=status.HTTP_200_OK
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"message": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = True
        user.save()

        django_rq.get_queue('default').enqueue(send_welcome_email, user.email)

        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK
        )


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            users = User.objects.filter(email=email, is_active=True) # only registered and active users

            # security check, no response weather user exists or not
            for user in users:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5500')
                password_reset_link = f"{frontend_url}/password_confirm/{uid}/{token}/"

                django_rq.get_queue('default').enqueue(
                    send_user_email,
                    user,
                    subject="Reset your password",
                    template_name="reset_password",
                    link_name="password_reset_link",
                    link_value=password_reset_link
                )

            return Response(
                {"detail": "If this email exists, a password reset link has been sent."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = ConfirmPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except Exception:
                return Response({"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return Response(
                {"detail": "Your password has been successfully reset."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return None  # no Token => not authenticated
        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid token")


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get user information after validation
        user = serializer.user

        # get both tokens
        refresh = serializer.validated_data["refresh"] # get refresh token
        access = serializer.validated_data["access"] # get access token

        response = Response(
            {
            "detail":"Login successfully!",
            "user": {
                    "id": user.pk,
                    "username": user.username,
                    "email": user.email
                }
            }
        )

        response.set_cookie(
            key = "access_token",
            value = str(access),
            httponly = True,
            secure = True,
            samesite = "Lax"
        )

        response.set_cookie(
            key = "refresh_token",
            value = str(refresh),
            httponly = True,
            secure = True,
            samesite = "Lax"
        )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail":"Refresh Token not found."}, status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(
            data = {"refresh": refresh_token}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response(
                {"detail":"Refresh Token invalid"}, status=status.HTTP_401_UNAUTHORIZED,
            )
        
        access_token = serializer.validated_data.get("access")

        response = Response(
            {
                "detail":"Token refreshed",
                "access": access_token
            }
        )

        response.set_cookie(
            key = "access_token",
            value = access_token,
            httponly = True,
            secure = True,
            samesite = "Lax"
        )

        return response


class LogoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )
        
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response