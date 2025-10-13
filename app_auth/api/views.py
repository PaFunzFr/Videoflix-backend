import os
import django_rq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .utils import send_activation_email, send_welcome_email

from dotenv import load_dotenv
load_dotenv()

User = get_user_model()

from .serializers import RegisterSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5500')
            activation_link = f"{frontend_url}/api/activate/{uid}/{token}/"

            django_rq.get_queue('default').enqueue(send_activation_email, user, activation_link)

            return Response(
                {"user": {"id": user.pk, "email": user.email}, "token": token},
                status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
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


