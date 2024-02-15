from celery import shared_task
from djangopoc import settings
from django.core.mail import send_mail
from core.models import CustomUser
from farmer.models import ICOEntity


@shared_task
def broadcast_newico_email(name, crop, capital, closes_on):

    # print(name, crop, capital, closes_on)
    investors = CustomUser.objects.filter(user_type='I')
    closes_on_date = closes_on.date()
    print('Date: ', closes_on_date)

    for investor in investors:
        subject = 'New ICO Arrived'
        message = f'Hi {investor.first_name}, We would like to inform you about arrival of a new ICO, Farmer {name}\'s {crop} ICO is raising a funding of {capital} Rs. Buy fast the ICO closes on {closes_on_date}.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [investor.email]
        print("sending mail using celery...", investor.first_name, investor.email)
        send_mail(subject, message, from_email, recipient_list, fail_silently=True)

@shared_task
def ico_rejection_email(name, mail, crop, reason):
    subject = 'ICO Rejected'
    message = f'Hi {name}, We regret to inform you that the recent {crop} ICO created by you has been rejected, because of the reason: {reason}. Please update the ICO for verification with necessary changes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    print("sending ICO rejection mail using celery...", name, mail)
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)

@shared_task
def farmer_verified_email(name, mail):

    subject = 'Account Verified'
    message = f'Hi {name}, Congratulations your account has been verified by us. You can now create ICOs and raise funding for your crops.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    print("sending mail using celery...", name, mail)
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)

@shared_task
def farmer_rejection_email(name, mail, reason):
    subject = 'Farmer Account Rejection'
    message = f'Hi {name}, We regret to inform you that your account verification failed, because of the reason: {reason}. Please update your account details for verification with necessary changes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    print("sending Farmer account rejection mail using celery...", name, mail)
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)


@shared_task
def investor_verified_email(name, mail):

    subject = 'Account Verified'
    message = f'Hi {name}, Congratulations your account has been verified by us. You can now buy ICOs and help farmers by investing.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    print("sending mail using celery...", name, mail)
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)

@shared_task
def investor_rejection_email(name, mail, reason):
    subject = 'Investor Account Rejection'
    message = f'Hi {name}, We regret to inform you that your account verification failed, because of the reason: {reason}. Please update your account details for verification with necessary changes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    print("sending Investor account rejection mail using celery...", name, mail)
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)


@shared_task
def investor_forced_return_email(name, mail, return_amt, crop, farmer_name, investment_amt):

    subject = 'Return Recieved'
    message = f'Hi {name}, your wallet has been credited with {return_amt} Rs from {farmer_name}\'s {crop} ICO in which you invested {investment_amt}, we apologize for the delay caused from the farmers end.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [mail]
    print("sending mail using celery...", name, mail)
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)