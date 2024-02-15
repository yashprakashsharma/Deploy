from celery import shared_task
from djangopoc import settings
from django.core.mail import send_mail
from core.models import CustomUser
from farmer.models import ICOEntity


@shared_task
def investor_return_email(name, mail, return_amt, crop, farmer_name, investment_amt):

    rounded_return_amt = round(return_amt, 2)
    rounded_investment_amt = round(investment_amt, 2)

    subject = 'Return Recieved'
    message = f'Hi {name}, your wallet has been credited with {rounded_return_amt} Rs from {farmer_name}\'s {crop} ICO in which you invested {rounded_investment_amt}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    print("sending mail using celery...", name, mail)
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)





