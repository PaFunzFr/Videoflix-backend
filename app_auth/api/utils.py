from django.conf import settings
import os
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string

from dotenv import load_dotenv
load_dotenv()

def attach_logo(msg):
    image_path = os.path.join(settings.BASE_DIR, 'app_auth', 'static', 'app_auth', 'logo_icon.png')
    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read())
        img.add_header('Content-ID', '<logo_cid>')
        img.add_header('Content-Disposition', 'inline', filename='logo_icon.png')
        msg.attach(img)


def send_user_email(user, subject, template_name, link_name, link_value):
    from_email = os.getenv("DEFAULT_FROM_EMAIL")
    site_url = os.getenv("FRONTEND_URL", "http://localhost:8000")

    context = {
        'user': user,
        link_name: link_value,
        'site_url': site_url,
        'logo_cid': 'logo_cid',
    }
    text_content = render_to_string(f"{template_name}.txt", context)
    html_content = render_to_string(f"{template_name}.html", context)
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        [user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    attach_logo(msg)
    msg.send(fail_silently=False)


def send_welcome_email(user):
    print("Welcome to Videoflix")