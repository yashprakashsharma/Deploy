from celery import shared_task
from djangopoc import settings
from django.core.mail import send_mail
from core.models import Investor
from farmer.models import ICOEntity

@shared_task
def test_func(a, b, c):
    # operations
    print("start...")
    print(a, type(a))
    print(b, type(b))
    print(c, type(c))
    print("end...")
    return "Done"

@shared_task
def send_purchase_confirmation_email(name, to_mail, quantity, total_cost, ico_entity_id):
    print('at begin')
    ico_entity = ICOEntity.objects.get(pk=ico_entity_id)
    print('found it', ico_entity.crop)
    # Round the total_cost to 2 decimal places
    rounded_total_cost = round(total_cost, 2)

    subject = 'ICO Purchase Confirmation'
    message = f'Thank you {name} for purchasing {quantity} units of Farmer {ico_entity.farmer.user.first_name}\'s {ico_entity.crop} crop ICO having id: {ico_entity.id}. You successfully paid {rounded_total_cost} Rs.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [to_mail]
    print("sending mail using celery...")
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)