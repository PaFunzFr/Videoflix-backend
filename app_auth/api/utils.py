from django.conf import settings
import os
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string

from dotenv import load_dotenv
load_dotenv()

def send_activation_email(user, activation_link):

    from_email = os.getenv("DEFAULT_FROM_EMAIL")
    site_url = os.getenv("FRONTEND_URL", "http://localhost:8000")
    image_path = os.path.join(settings.BASE_DIR, 'app_auth', 'static', 'app_auth', 'logo_icon.png')

    context = {
        'user': user,
        'activation_link': activation_link,
        'site_url': site_url,
        'logo_cid': 'logo_cid',
    }
    text_content = render_to_string(
        'confirm_account.txt', context)
    html_content = render_to_string(
        'confirm_account.html', context)
    
    msg = EmailMultiAlternatives(
        "Confirm your account",
        text_content,
        from_email,
        [user.email],
    )

    msg.attach_alternative(html_content, "text/html")

    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read())
        img.add_header('Content-ID', '<logo_cid>')
        img.add_header('Content-Disposition', 'inline', filename='logo_icon.png')
        msg.attach(img)
    msg.send(fail_silently=False)

def send_password_reset_email(user, password_reset_link):
    print("Email for password reset was sent")

def send_welcome_email(user):
    print("Welcome to Videoflix")