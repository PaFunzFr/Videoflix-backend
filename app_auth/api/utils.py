from django.core.mail import send_mail
from django.conf import settings

def send_activation_email(user, activation_link):
    print("Email for activation was sent")

def send_password_reset_email(user, password_reset_link):
    print("Email for password reset was sent")

def send_welcome_email(user):
    print("Welcome to Videoflix")