import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from dotenv import load_dotenv
load_dotenv()

# send_mail(
#     "Subject here",
#     "Here is the message.",
#     "from@example.com",
#     ["to@example.com"],
#     fail_silently=False,
# )

def send_activation_email(user, activation_link):
    from_email = os.getenv("DEFAULT_FROM_EMAIL")
    site_url = os.getenv("FRONTEND_URL", "http://localhost:8000") 
    context = {
        'user': user,
        'activation_link': activation_link,
        'site_url': site_url,
        'logo_url': f"{site_url}/media/templates/logo_icon.svg",
    }
    text_content = render_to_string(
        'confirm_account.txt', context)
    html_content = render_to_string(
        'confirm_account.html', context)
    
    # Then, create a multipart email instance.
    msg = EmailMultiAlternatives(
        "Confirm your account",
        text_content,
        from_email,
        [user.email], #change for testing 
    )

    # Lastly, attach the HTML content to the email instance and send.
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_password_reset_email(user, password_reset_link):
    print("Email for password reset was sent")

def send_welcome_email(user):
    print("Welcome to Videoflix")