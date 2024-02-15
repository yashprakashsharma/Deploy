from celery import shared_task
from djangopoc import settings
from django.core.mail import send_mail


@shared_task
def send_otp(subject, message, receiver):

    from_email = settings.EMAIL_HOST_USER

    print("sending otp mail using celery...")
    print("got: ", subject, message, receiver)
    send_mail(subject, message, from_email, receiver, fail_silently=True)





