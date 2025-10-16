import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from .utils import queue_send_confirm_mail, queue_send_reset_mail, queue_send_welcome_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from drf_spectacular.utils import extend_schema, OpenApiResponse

from dotenv import load_dotenv
load_dotenv()

User = get_user_model()

from .authentications import CookieJWTAuthentication
from .serializers import (
    RegisterSerializer,
    RequestPasswordResetSerializer,
    ConfirmPasswordSerializer,
    LoginSerializer
)


@extend_schema(
    description="Register a new user account and send an email confirmation link.",
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(description="User created successfully."),
        400: OpenApiResponse(description="Invalid registration data."),
    },
)
class RegisterView(APIView):
    """
    API endpoint for user registration.
    After successful registration, a confirmation email is sent to the user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5500')
            activation_link = f"{frontend_url}/pages/auth/activate.html?uid={uid}&token={token}"

            queue_send_confirm_mail(user, activation_link)

            return Response(
                {"user": {"id": user.pk, "email": user.email}, "token": token},
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="Activate a user account using a token received via email.",
    responses={
        200: OpenApiResponse(description="Account activated successfully."),
        400: OpenApiResponse(description="Invalid or expired activation token."),
    },
)
class ActivateView(APIView):
    """
    API endpoint for account activation via an emailed token.
    """

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

        queue_send_welcome_mail(user)

        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK
        )


@extend_schema(
    description="Request a password reset link. A reset email will be sent if the email exists.",
    request=RequestPasswordResetSerializer,
    responses={
        200: OpenApiResponse(description="Password reset email sent if account exists."),
        400: OpenApiResponse(description="Invalid input data."),
    },
)
class RequestPasswordResetView(APIView):
    """
    API endpoint for requesting a password reset link.
    For security reasons, the response does not indicate whether the email exists or not.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email, is_active=True) # only registered and active users

        # security check, no response weather user exists or not
        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5500')
            password_reset_link = f"{frontend_url}/pages/auth/confirm_password.html?uid={uid}&token={token}"

            queue_send_reset_mail(user, password_reset_link)

        return Response(
            {"detail": "If this email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK
        )


@extend_schema(
    description="Confirm a password reset by providing a valid token and new password.",
    request=ConfirmPasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password successfully reset."),
        400: OpenApiResponse(description="Invalid token or reset link."),
    },
)
class ConfirmPasswordView(APIView):
    """
    API endpoint for confirming a password reset and setting a new password.
    """

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = ConfirmPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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


@extend_schema(
    description="Authenticate a user and set JWT tokens as secure cookies.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Login successful. Tokens set in cookies."),
        401: OpenApiResponse(description="Invalid credentials."),
    },
)
class LoginView(TokenObtainPairView):
    """
    API endpoint for logging in a user.
    Returns JWT access and refresh tokens as secure HTTP-only cookies.
    """

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
            samesite = "None" # "Lax/None" -> localhost could be an issue
        )

        response.set_cookie(
            key = "refresh_token",
            value = str(refresh),
            httponly = True,
            secure = True,
            samesite = "None" # "Lax/None" -> localhost could be an issue
        )

        return response


@extend_schema(
    description="Refresh the access token using a valid refresh token from cookies.",
    responses={
        200: OpenApiResponse(description="Access token refreshed successfully."),
        401: OpenApiResponse(description="Missing or invalid refresh token."),
    },
)
class CookieTokenRefreshView(TokenRefreshView):
    """
    API endpoint for refreshing the JWT access token using the refresh token stored in cookies.
    """

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
            samesite = "None" # "Lax/None" -> localhost could be an issue
        )

        return response


@extend_schema(
    description="Logout the user by deleting authentication cookies.",
    responses={200: OpenApiResponse(description="User logged out successfully.")},
)
class LogoutView(APIView):
    """
    API endpoint for logging out a user by deleting their JWT cookies.
    """
    
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