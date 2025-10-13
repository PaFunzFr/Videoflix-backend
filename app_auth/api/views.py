import os
import django_rq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .utils import send_user_email, send_welcome_email

from dotenv import load_dotenv
load_dotenv()

User = get_user_model()

from .serializers import RegisterSerializer, RequestPasswordResetSerializer, ConfirmPasswordSerializer

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