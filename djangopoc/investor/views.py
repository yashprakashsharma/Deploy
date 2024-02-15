from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta,datetime
from django.views import View
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, F, ExpressionWrapper, FloatField
from djangopoc import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.decorators import method_decorator
from core.decorators import login_and_investor_required, investor_verified
from core.models import Investor
from farmer.models import ICOEntity, FarmerHistory
from investor.models import ICOTransactions
from investor.forms import BuyICOForm
from core.forms import InvestorRegistrationForm
from investor.tasks import test_func, send_purchase_confirmation_email


# Create your views here.

# def send_purchase_confirmation_email(investor, quantity, total_cost, ico_entity):
#     subject = 'ICO Purchase Confirmation'
#     message = f'Thank you {investor.user.first_name} for purchasing {quantity} units of Farmer {ico_entity.farmer.user.first_name}\'s {ico_entity.crop} crop ICO having id: {ico_entity.id}. You successfully paid {total_cost} Rs.'
#     from_email = settings.EMAIL_HOST_USER
#     recipient_list = [investor.user.email]
#     print( subject, message, from_email, recipient_list)

#     send_mail(subject, message, from_email, recipient_list, fail_silently=True)

@never_cache
@login_and_investor_required
def home_investor(request):
    # print(request.user.first_name, request.user.email, 12)
    # test_func.delay(request.user.first_name, request.user.email, 12)
    return render(request, 'investor/home_investor.html', {'user': request.user})

@never_cache
@login_and_investor_required
def notverified_investor(request):
    return render(request, 'investor/investor_not_verified.html', {'user': request.user})

@never_cache
@login_and_investor_required
def investor_profile(request):
    investor = Investor.objects.get(user=request.user)
    context = {
        'user': request.user,
        'investor': investor,
    }
    return render(request, 'investor/investor_profile.html', context)

@never_cache
@investor_verified
def investor_wallet(request):
    investor = Investor.objects.get(user=request.user)
    investor_wallet = investor.wallet
    return render(request, 'investor/investor_wallet.html', {'wallet': investor_wallet})

@never_cache
@investor_verified
def deposit_money(request):
    investor = Investor.objects.get(user=request.user)
    investor_wallet = investor.wallet
    if request.method == 'POST':
        # print(type(request.POST['amount']))
        credit_card = request.POST.get('credit_card')
        cardholder_name = request.POST.get('cardholder_name')
        cvv = request.POST.get('cvv')
        expiration_date = request.POST.get('expiration_date')
        print('we got: ', credit_card, cardholder_name, cvv, expiration_date)

        # checks
        errors = {}
        if not is_valid_credit_card(credit_card):
            errors['credit_card'] = 'Invalid credit card number.'
        if not is_valid_expiration_date(expiration_date):
            errors['expiration_date'] = 'Invalid Exp. Date'
        
        if errors:
            form_data = {
                'credit_card': credit_card,
                'cardholder_name': cardholder_name,
                'cvv': cvv,
                'expiration_date': expiration_date,
                'amount': request.POST.get('amount'),
            }
            return render(request, 'investor/deposit_money.html', {'errors': errors, 'form_data': form_data})
        # main functionality
        amount = float(request.POST.get('amount'))
        # print('will work!')
        investor_wallet.deposit(amount)
        return redirect(reverse('investor:investor_wallet'))
    return render(request, 'investor/deposit_money.html')

def is_valid_credit_card(credit_card):
    card_number = int(credit_card)
    if card_number == 0: return False
    idx = 0
    total_sum = 0
    while card_number > 0:
        digit = card_number % 10
        if idx%2==1: 
            digit *= 2
            if digit >= 10:
                digit = digit % 10 + digit // 10
        total_sum += digit
        card_number //= 10
        idx += 1
    return bool(total_sum % 10 == 0 and len(credit_card) == 16 and credit_card.isdigit())


# def is_valid_cvv(cvv):
#     return len(cvv) == 3 and cvv.isdigit()

def is_valid_expiration_date(expiration_date):
    if len(expiration_date) != 5:
        return False
    if not expiration_date[:2].isdigit() or not expiration_date[3:].isdigit():
        return False
    month = int(expiration_date[:2])
    year = int(expiration_date[3:])
    if not 1 <= month <= 12:
        return False
    current_year = datetime.now().year % 100
    if year < current_year or (year == current_year and month < datetime.now().month):
        return False
    if year > current_year+10:
        return False
    return True


# @never_cache
@method_decorator(login_and_investor_required, name='dispatch')
class InvestorICOListView(View):
    template_name = 'investor/show_icos.html'
    items_per_page = 5

    def get(self, request, *args, **kwargs):
        # Get all verified and active ICOs
        search_query = request.GET.get('search', '')
        icos = ICOEntity().verified_and_active_entities

        # Apply filter based on form inputs
        crop_name = request.GET.get('crop_name', '')
        farmer_name = request.GET.get('farmer_name', '')
        max_price = request.GET.get('max_price', '')
        # min_price = request.GET.get('min_price', '')
        close_date = request.GET.get('close_date', '')
        return_date = request.GET.get('return_date', '')
        # print('we have' ,max_price, type(max_price))

        if crop_name:
            icos = icos.filter(crop__icontains=crop_name)
        if farmer_name:
            icos = icos.filter(farmer__user__first_name__icontains=farmer_name)
        if max_price:
            icos = icos = icos.annotate(
                calculated_price=ExpressionWrapper(F('capital') / F('quantity'), output_field=FloatField())
            ).filter(calculated_price__lte=max_price)
        # if min_price:
        #     icos = icos.annotate(
        #         calculated_price=ExpressionWrapper(F('capital') / F('quantity'), output_field=FloatField())
        #     ).filter(calculated_price__gte=min_price)
        if close_date:
            try: 
                close_date = timezone.datetime.strptime(close_date, '%Y-%m-%d')
                # Set the time to just a minute before midnight
                close_date = close_date.replace(hour=23, minute=59, second=59)
                # Make close_date timezone-aware
                close_date = timezone.make_aware(close_date)
                # print('now it is: ', close_date, type(close_date))
                icos = icos.filter(closes_on__lte=close_date)
            except ValueError:
                # Handle the case where the close_date string is not a valid date
                print('Invalid date format')
        if return_date:
            try: 
                return_date = timezone.datetime.strptime(return_date, '%Y-%m-%d')
                # Set the time to just a minute before midnight
                return_date = return_date.replace(hour=23, minute=59, second=59)
                # Make close_date timezone-aware
                return_date = timezone.make_aware(return_date)
                # print('now it is: ', close_date, type(close_date))
                icos = icos.filter(return_date__lte=return_date)
            except ValueError:
                # Handle the case where the close_date string is not a valid date
                print('Invalid date format')


        # Apply search filter if search_query is present
        if search_query:
            icos = icos.filter(
                Q(crop__icontains=search_query) | Q(farmer__user__first_name__icontains=search_query) | Q(farmer__user__username__icontains=search_query)
            )

        paginator = Paginator(icos, self.items_per_page)
        page = request.GET.get('page')

        try:
            icos = paginator.page(page)
        except PageNotAnInteger:
            # If the page parameter is not an integer, deliver the first page.
            icos = paginator.page(1)
        except EmptyPage:
            # If the page is out of range (e.g., 9999), deliver the last page.
            icos = paginator.page(paginator.num_pages)

        context = {'icos': icos}
        return render(request, self.template_name, context)

@never_cache    
@investor_verified
def buy_ico(request, ico_id):
    investor = get_object_or_404(Investor, user=request.user)
    ico_entity = get_object_or_404(ICOEntity, pk=ico_id)

    form = BuyICOForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        quantity = form.cleaned_data['quantity']

        with transaction.atomic():
            
            ico_entity = ICOEntity.objects.select_for_update().get(pk=ico_entity.pk)

            if quantity > 0 and quantity <= ico_entity.stock_available:
                total_cost = ico_entity.price * quantity
                print('Total cost: ', total_cost)

                if investor.wallet.balance >= total_cost:

                    # Check if there's an existing transaction
                    existing_transaction = ICOTransactions.objects.filter(
                        ico=ico_entity,
                        investor=investor
                    ).first()

                    if existing_transaction:
                        # Update the existing transaction's quantity
                        existing_transaction.quantity += quantity
                        existing_transaction.save()
                    else:
                        # Create a new transaction entry
                        ICOTransactions.objects.create(
                            ico=ico_entity,
                            investor=investor,
                            quantity=quantity,
                            per_entity_cost=ico_entity.price,
                        )

                    # Once Txn is created or updated we deduct wallet balance and update ico_entity
                    investor.wallet.withdraw(total_cost)
                    ico_entity.farmer.wallet.deposit(total_cost)
                    ico_entity.sold_quantity += quantity
                    ico_entity.save()
                    # Schedule the email to be sent after the transaction is committed
                    # transaction.on_commit(lambda: send_purchase_confirmation_email(investor, quantity, total_cost, ico_entity))
                    transaction.on_commit(lambda: send_purchase_confirmation_email.delay(investor.user.first_name, investor.user.email, quantity, total_cost, ico_entity.id))


                    return redirect(reverse('investor:investor_icos'))

                else:
                    form.add_error(None, 'Insufficient funds in your wallet.')
            else:
                form.add_error(None, 'Invalid quantity or not enough stocks available.')

    return render(request, 'investor/buy_ico.html', {'ico_entity': ico_entity, 'form': form})

@never_cache
@investor_verified
def investor_icos(request):
    investor = request.user.investor  # Assuming you have a user profile linked to Investor

    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')
    current_datetime = timezone.now()
    
    print(filter_type)
    if filter_type == "open":
        transactions = ICOTransactions.objects.filter(
            investor=investor,
            ico__closes_on__gte=current_datetime
        )
    elif filter_type == "closed":
        transactions = ICOTransactions.objects.filter(
            investor=investor,
            ico__return_date__lt=current_datetime
        )
    elif filter_type == "pending":
        transactions = ICOTransactions.objects.filter(
            investor=investor,
            ico__closes_on__lte=current_datetime,
            ico__return_date__gte=current_datetime
        )
    else:
        transactions = ICOTransactions.objects.filter(investor=investor)

     # Apply search filter if search_query is present
    if search_query:
        transactions = transactions.filter(
            Q(ico__crop__icontains=search_query) | Q(ico__farmer__user__first_name__icontains=search_query)
        )

    items_per_page = 5

    paginator = Paginator(transactions, items_per_page)
    page = request.GET.get('page')

    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, deliver the first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page.
        transactions = paginator.page(paginator.num_pages)

    context = {
        'investor': investor,
        'transactions': transactions,
        'filter_type': filter_type,
    }

    return render(request, 'investor/investor_icos.html', context)

@never_cache
@login_and_investor_required
def ico_details(request, ico_id):
    ico = ICOEntity.objects.get(pk=ico_id)
    history = FarmerHistory.objects.filter(farmer=ico.farmer)
    context = {
        'ico': ico,
        'history': history,
    }
    return render(request, 'investor/ico_detail.html', context)

# @never_cache
@method_decorator(login_and_investor_required, name='dispatch')
class InvestorEditView(View):
    template_name = 'investor/edit_investor.html'

    def get(self, request):
        investor = Investor.objects.get(user=request.user)
        form = InvestorRegistrationForm(instance=investor)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        investor = Investor.objects.get(user=request.user)
        form = InvestorRegistrationForm(request.POST, request.FILES, instance=investor)
        if form.is_valid():
            form.save()
            investor.is_rejected = False
            investor.rejection_reason = ''
            investor.save()
            return redirect('investor:investor_profile')  # Redirect to the investor profile page
        return render(request, self.template_name, {'form': form})