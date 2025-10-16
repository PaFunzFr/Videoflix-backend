"""
email_utils.py
---------------
This module provides asynchronous email-sending functionality for the Videoflix application.  
It leverages `django_rq` for background job processing and Django's email framework 
for constructing and sending rich HTML and text-based emails.  

Emails include account confirmation, password reset, and welcome messages.  
Each email embeds the Videoflix logo and uses pre-defined Django templates.

Functions:
    queue_send_confirm_mail(user, link): Queues an account confirmation email.
    queue_send_reset_mail(user, link): Queues a password reset email.
    queue_send_welcome_mail(user): Queues a welcome email after successful account activation.
    attach_logo(msg): Embeds the Videoflix logo into an outgoing email.
    send_user_email(user, subject, template_name, link_name, link_value): 
        Core email-sending utility used by the queued functions.
"""

from django.conf import settings
import os
import django_rq
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string

from dotenv import load_dotenv
load_dotenv()


def queue_send_confirm_mail(user, link):
    """
    Queue an account confirmation email to be sent asynchronously.

    This function enqueues a background job using Django RQ to send
    an account confirmation email with a unique activation link.

    Args:
        user (User): The user instance to whom the email will be sent.
        link (str): The activation link for confirming the user's account.
    """
    django_rq.get_queue('default').enqueue(
        send_user_email,
        user,
        subject="Confirm your account",
        template_name="confirm_account",
        link_name="activation_link",
        link_value=link
    )


def queue_send_reset_mail(user, link):
    """
    Queue a password reset email to be sent asynchronously.

    This function enqueues a background job using Django RQ to send
    a password reset email containing a secure reset link.

    Args:
        user (User): The user instance requesting a password reset.
        link (str): The password reset link sent to the user's email.
    """
    django_rq.get_queue('default').enqueue(
        send_user_email,
        user,
        subject="Reset your password",
        template_name="reset_password",
        link_name="password_reset_link",
        link_value=link
    )


def queue_send_welcome_mail(user):
    """
    Queue a welcome email to be sent asynchronously.

    This function enqueues a background job to send a personalized
    welcome email after a user has successfully activated their account.

    Args:
        user (User): The user instance that has just activated their account.
    """
    django_rq.get_queue('default').enqueue(
        send_user_email,
        user,
        subject="Welcome to Videoflix",
        template_name="welcome_message",
        link_name="",
        link_value=""
    )


def attach_logo(msg):
    """
    Attach the Videoflix logo image to an email message.

    The logo is embedded inline and referenced by a Content-ID (`logo_cid`)
    so that it can be displayed directly in HTML email templates.

    Args:
        msg (EmailMultiAlternatives): The email message object to which the logo is attached.
    """
    image_path = os.path.join(settings.BASE_DIR, 'app_auth', 'logo', 'app_auth', 'logo_icon.png')
    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read())
        img.add_header('Content-ID', '<logo_cid>')
        img.add_header('Content-Disposition', 'inline', filename='logo_icon.png')
        msg.attach(img)


def send_user_email(user, subject, template_name, link_name, link_value):
    """
    Send an email to a user using text and HTML templates.

    This is the core email-sending function, which renders templates,
    attaches an inline logo, and sends the message. It supports both
    plain-text and HTML content and is typically executed asynchronously
    through an RQ worker.

    Args:
        user (User): The recipient user instance.
        subject (str): The subject line of the email.
        template_name (str): Base name of the email template (without extension).
        link_name (str): The context variable name used for the link in the email template.
        link_value (str): The actual URL or token value to be injected into the template.

    Raises:
        Exception: Propagates any error encountered during email rendering or sending.
    """
    from_email = os.getenv("DEFAULT_FROM_EMAIL")
    site_url = os.getenv("FRONTEND_URL", "http://localhost:8000")

    context = {
        'user': user,
        link_name: link_value,
        'site_url': site_url,
        'logo_cid': 'logo_cid',
    }
    
    # Render text and HTML versions of the email
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