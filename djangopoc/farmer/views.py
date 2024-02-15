from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta,datetime
from django.db.models import Sum, Q
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from core.decorators import login_and_farmer_required, farmer_verified
from core.models import Farmer
from farmer.forms import FarmerHistoryForm, ICOEntityForm, ICOReturnsForm
from core.forms import FarmerRegistrationForm
from farmer.models import FarmerHistory, ICOEntity
from investor.models import ICOTransactions
from farmer.tasks import investor_return_email

# Create your views here.
@never_cache
@login_and_farmer_required
def home_farmer(request):
    return render(request, 'farmer/home_farmer.html', {'user': request.user})

@never_cache
@login_and_farmer_required
def notverified_farmer(request):
    return render(request, 'farmer/farmer_not_verified.html', {'user': request.user})

@never_cache
@login_and_farmer_required
def farmer_profile(request):
    farmer = Farmer.objects.get(user=request.user)
    context = {
        'user': request.user,
        'farmer': farmer,
    }
    return render(request, 'farmer/farmer_profile.html', context)

@never_cache
@farmer_verified
def farmer_wallet(request):
    farmer = Farmer.objects.get(user=request.user)
    farmer_wallet = farmer.wallet
    return render(request, 'farmer/farmer_wallet.html', {'wallet': farmer_wallet})

@never_cache
@farmer_verified
def deposit_money(request):
    farmer = Farmer.objects.get(user=request.user)
    farmer_wallet = farmer.wallet
    if request.method == 'POST':
        # print(type(request.POST['amount']))
        credit_card = request.POST.get('credit_card')
        cardholder_name = request.POST.get('cardholder_name')
        cvv = request.POST.get('cvv')
        expiration_date = request.POST.get('expiration_date')
        print('we got: ', credit_card, cardholder_name, cvv, expiration_date)

        #checks
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
            return render(request, 'farmer/deposit_money.html', {'errors': errors, 'form_data': form_data})

        # main functionality
        amount = float(request.POST.get('amount'))
        farmer_wallet.deposit(amount)
        return redirect(reverse('farmer:farmer_wallet'))
    return render(request, 'farmer/deposit_money.html')

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

@never_cache
@login_and_farmer_required
def add_farmer_history(request):
    if request.method == 'POST':
        form = FarmerHistoryForm(request.POST)
        if form.is_valid():
            farmer = get_object_or_404(Farmer, user=request.user)
            area_cultivated = form.cleaned_data['area_cultivated']

             # Check if the sum of area_cultivated exceeds land_area
            total_area_cultivated = FarmerHistory.objects.filter(
                farmer=farmer,
                year=form.cleaned_data['year'],
                season=form.cleaned_data['season']
            ).aggregate(Sum('area_cultivated'))['area_cultivated__sum'] or 0.0

            # print('our total area: ', total_area_cultivated, type(total_area_cultivated))
            if total_area_cultivated + area_cultivated > farmer.land_area:
                form.add_error(None, 'Not enough land_area')
            else:
                history_entry = form.save(commit=False)
                history_entry.farmer = farmer
                history_entry.save()
                return redirect('farmer:farmer_profile')
    else:
        form = FarmerHistoryForm()
    

    return render(request, 'farmer/add_farmer_history.html', {'form': form})

@never_cache
@login_and_farmer_required
def edit_farmer_history(request, history_id):
    history_entry = get_object_or_404(FarmerHistory, id=history_id)
    if request.method == 'POST':
        form = FarmerHistoryForm(request.POST, instance=history_entry)
        if form.is_valid():
            farmer = get_object_or_404(Farmer, user=request.user)
            area_cultivated = form.cleaned_data['area_cultivated']

            # Check if the sum of area_cultivated exceeds land_area
            total_area_cultivated = FarmerHistory.objects.filter(
                farmer=farmer,
                year=form.cleaned_data['year'],
                season=form.cleaned_data['season']
            ).exclude(id=history_id).aggregate(Sum('area_cultivated'))['area_cultivated__sum'] or 0.0

            # print('our total area: ', total_area_cultivated, type(total_area_cultivated))
            # print('area cult: ', area_cultivated)
            # print('farmer area cult: ', farmer.land_area)
            # print(total_area_cultivated + area_cultivated > farmer.land_area)
            if total_area_cultivated + area_cultivated > farmer.land_area:
                form.add_error(None, 'Not enough land_area')
            else:
                form.save()
                return redirect('farmer:farmer_profile')
    else:
        form = FarmerHistoryForm(instance=history_entry)

    return render(request, 'farmer/edit_farmer_history.html', {'form': form, 'history_entry': history_entry})

@never_cache
@farmer_verified
def add_ico_entity(request):
    if request.method == 'POST':
        form = ICOEntityForm(request.POST)
        if form.is_valid():
            farmer = get_object_or_404(Farmer, user=request.user)
            new_entity_land_area = form.cleaned_data['land_area']
            capital = form.cleaned_data['capital'] 
            quantity = form.cleaned_data['quantity']
            cost = capital/quantity
            
            # Check if the total land_area of "Open" and "Pending" ICOEntities plus the new_entity_land_area exceeds farmer's land_area
            current_datetime = timezone.now()
            total_open_pending_land_area = ICOEntity.objects.filter(
                farmer=farmer,
                isVerified=True,
                created_at__lt=current_datetime,
                return_date__gt=current_datetime,
            ).aggregate(Sum('land_area'))['land_area__sum'] or 0
            print('already acquired: ' ,total_open_pending_land_area)
            print('price: ' , cost, type(cost))

            if new_entity_land_area + total_open_pending_land_area > farmer.land_area:
                form.add_error(None, 'Not enough land area')
            elif cost<50.0:
                form.add_error(None, 'Each share should cost > 50Rs')
            else:
                ico_entity = form.save(commit=False)
                ico_entity.farmer = farmer
                ico_entity.save()
                redirect_url = reverse('farmer:ico_details', kwargs={'ico_id': ico_entity.pk})
                return redirect(redirect_url)  # Adjust the redirect URL as needed
    else:
        form = ICOEntityForm()

    return render(request, 'farmer/create_ico.html', {'form': form})

# @never_cache
@method_decorator(farmer_verified, name='dispatch')
class ICOListView(View):
    template_name = 'farmer/show_farmer_icos.html'
    items_per_page = 5

    def get(self, request, *args, **kwargs):
        # Get user-selected filter from the query parameters
        filter_type = request.GET.get('filter', 'all')
        search_query = request.GET.get('search', '')

        current_datetime = timezone.now()

        # Apply filters based on the user's choice
        if filter_type == 'verified':
            icos = ICOEntity.objects.filter(farmer=request.user.farmer , isVerified=True)
        elif filter_type == 'not_verified':
            icos = ICOEntity.objects.filter(farmer=request.user.farmer, isVerified=False)
        elif filter_type == 'open':
            icos = ICOEntity.objects.filter(farmer=request.user.farmer, isVerified=True, closes_on__gte=current_datetime)
        elif filter_type == 'closed':
            icos = ICOEntity.objects.filter(farmer=request.user.farmer, isVerified=True, return_date__lt=current_datetime)
        elif filter_type == 'pending':
            icos = ICOEntity.objects.filter(
                farmer=request.user.farmer, 
                isVerified=True,
                closes_on__lte=current_datetime,
                return_date__gte=current_datetime
            )
        elif filter_type == 'rejected':
            icos = ICOEntity.objects.filter(
                farmer=request.user.farmer, 
                isVerified=False,
                is_rejected=True
            )
        else:
            # Default to showing all ICOs
            icos = ICOEntity.objects.filter(farmer=request.user.farmer)

        if search_query:
            icos = icos.filter(
                Q(crop__icontains=search_query)
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

        context = {'icos': icos, 'filter_type': filter_type, 'search_query': search_query}
        return render(request, self.template_name, context)

@never_cache    
@farmer_verified
def ico_details_view(request, ico_id):
    ico = ICOEntity.objects.get(pk=ico_id)
    return render(request, 'farmer/ico_detail.html', {'ico': ico})

@never_cache
@farmer_verified
def edit_ico_entity(request, ico_id):
    ico_entity = get_object_or_404(ICOEntity, pk=ico_id)
    # print('got', ico_entity)

    if request.method == 'POST':
        form = ICOEntityForm(request.POST, instance=ico_entity)
        if form.is_valid():
            new_entity_land_area = form.cleaned_data['land_area']
            capital = form.cleaned_data['capital'] 
            quantity = form.cleaned_data['quantity']
            cost = capital/quantity
            
            # Check if the total land_area of "Open" and "Pending" ICOEntities plus the new_entity_land_area exceeds farmer's land_area
            current_datetime = timezone.now()
            total_open_pending_land_area = ICOEntity.objects.filter(
                farmer=ico_entity.farmer,
                isVerified=True,
                created_at__lt=current_datetime,
                return_date__gt=current_datetime,
            ).exclude(id=ico_id).aggregate(Sum('land_area'))['land_area__sum'] or 0

            if new_entity_land_area + total_open_pending_land_area > ico_entity.farmer.land_area:
                form.add_error(None, 'Not enough land area')
            elif cost < 50.0:
                form.add_error(None, 'Each share should cost > 50Rs')
            else:
                form.save()
                ico_entity.is_rejected = False
                ico_entity.rejection_reason = ''
                ico_entity.save()
                redirect_url = reverse('farmer:ico_details', kwargs={'ico_id': ico_id})
                return redirect(redirect_url)

    else:
        form = ICOEntityForm(instance=ico_entity)

    return render(request, 'farmer/edit_ico_entity.html', {'form': form, 'ico_entity': ico_entity})

# @never_cache
@method_decorator(login_and_farmer_required, name='dispatch')
class FarmerEditView(View):
    template_name = 'farmer/edit_farmer.html'

    def get(self, request):
        farmer = Farmer.objects.get(user=request.user)
        form = FarmerRegistrationForm(instance=farmer)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        farmer = Farmer.objects.get(user=request.user)
        form = FarmerRegistrationForm(request.POST, request.FILES, instance=farmer)
        if form.is_valid():
            form.save()
            farmer.is_rejected = False
            farmer.rejection_reason = ''
            farmer.save()
            return redirect('farmer:farmer_profile')  # Redirect to the investor profile page
        return render(request, self.template_name, {'form': form})

@never_cache  
@farmer_verified  
def ico_returns(request, ico_id):
    ico = get_object_or_404(ICOEntity, pk=ico_id)

    if request.method == 'POST':
        form = ICOReturnsForm(request.POST)
        if form.is_valid():
            revenue = float(form.cleaned_data['revenue'])
            # print(revenue, type(revenue))
            farmer_balance = ico.farmer.wallet.balance
            investor_portion = revenue/2
            # print(investor_portion, type(investor_portion), ico.quantity, type(ico.quantity))
            investor_share = investor_portion/ico.quantity
            # print(investor_share, type(investor_share))
            total_quantity = ICOTransactions.objects.filter(ico_id=ico_id).aggregate(Sum('quantity'))['quantity__sum']
            # print(total_quantity, type(total_quantity))
            needed_balance = total_quantity*investor_share
            # print(needed_balance, type(needed_balance))
            if needed_balance <= farmer_balance:
                with transaction.atomic():
                    current_datetime = timezone.now()
                    investors = ICOTransactions.objects.filter(ico_id=ico_id)
                    for investor_transaction in investors:
                        shares_bought = investor_transaction.quantity
                        transfer_amount = investor_share * shares_bought
                        print('investor: ', shares_bought, transfer_amount)
                        print('farmer_wallet: ', ico.farmer.wallet.balance)
                        print('investor_wallet: ', investor_transaction.investor.wallet.balance)
                        print('mail: ', investor_transaction.investor.user.email)
                        ico.farmer.wallet.withdraw(transfer_amount)
                        investor_transaction.investor.wallet.deposit(transfer_amount)
                        investment_amount = shares_bought*investor_transaction.per_entity_cost
                        investor_return_email.delay(investor_transaction.investor.user.first_name, investor_transaction.investor.user.email, transfer_amount, ico.crop, ico.farmer.user.first_name, investment_amount)
                    
                    ico.return_date = current_datetime
                    ico.is_return_provided = True
                    ico.save()

                    # Create an entry in FarmerHistory
                    season = "Rabi" if current_datetime.month in [11, 12, 1, 2] else "Kharif"
                    year = current_datetime.year

                    # add a entry to farmer history
                    FarmerHistory.objects.create(
                        farmer=ico.farmer,
                        season=season,
                        year=year,
                        crop=ico.crop,
                        area_cultivated=ico.land_area,
                        revenue=investor_portion,
                        expenses=ico.capital
                    )
                return redirect('farmer:ico_details', ico_id)
            else:
                form.add_error(None, f'Not enough balance in the wallet. You need Rs {needed_balance} in your wallet while you have only Rs {farmer_balance}') 

    else:
        form = ICOReturnsForm()
    
    return render(request, 'farmer/ico_returns.html', {'form': form, 'ico': ico})