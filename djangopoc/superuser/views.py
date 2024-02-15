from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.urls import reverse
from core.decorators import login_and_user_type_required
from farmer.models import ICOEntity, FarmerHistory
from investor.models import ICOTransactions
from core.models import Farmer, Investor
from superuser.tasks import broadcast_newico_email, farmer_verified_email, investor_verified_email, investor_forced_return_email, ico_rejection_email, farmer_rejection_email, investor_rejection_email
from superuser.forms import ICORejectionForm, FarmerRejectionForm, InvestorRejectionForm
from datetime import timedelta

# Create your views here.
@never_cache
@login_and_user_type_required('S')
def home_superuser(request):
    # return HttpResponse('Bello SuperUser')
    return render(request, 'superuser/home_superuser.html', {'user': request.user})

@never_cache
@login_and_user_type_required('S')
def superuser_profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'superuser/superuser_profile.html', context)


#ICO related views here:
@never_cache
@login_and_user_type_required('S')
def show_icos(request):
    current_datetime = timezone.now()
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')

    # icos_list = ICOEntity.objects.all()
    # Filter based on the selected option
    if filter_type == 'not_verified':
        icos_list = ICOEntity.objects.filter(
            isVerified=False,
            is_rejected=False,
            closes_on__gte=current_datetime,
        )
    elif filter_type == 'defaulter':
        icos_list = ICOEntity.objects.filter(
            isVerified=True,
            is_return_provided = False,
            return_date__lte = current_datetime - timedelta(days=10),
        )
    else:
        icos_list = ICOEntity.objects.all()

     # Apply search filter if search_query is present
    if search_query:
        icos_list = icos_list.filter(
            Q(crop__icontains=search_query) | Q(farmer__user__first_name__icontains=search_query)
        )

    items_per_page = 5

    paginator = Paginator(icos_list, items_per_page)
    page = request.GET.get('page')

    try:
        icos = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, deliver the first page.
        icos = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page.
        icos = paginator.page(paginator.num_pages)

    context = {
        'icos': icos,
        'filter_type': filter_type,
    }
    return render(request, 'superuser/show_icos.html', context)

@never_cache
@login_and_user_type_required('S')
def ico_details(request, ico_id):
    ico = ICOEntity.objects.get(pk=ico_id)
    history = FarmerHistory.objects.filter(farmer=ico.farmer)
    form = ICORejectionForm(instance=ico)
    context = {
        'ico': ico,
        'history': history,
        'form': form,
    }
    return render(request, 'superuser/ico_detail.html', context)

@never_cache
@login_and_user_type_required('S')
def approve_ico(request, ico_id):
    ico = get_object_or_404(ICOEntity, pk=ico_id)
    ico.isVerified = True
    ico.save()
    broadcast_newico_email.delay(ico.farmer.user.first_name, ico.crop, ico.capital, ico.closes_on)
    # You can add additional logic or redirection here if needed
    return redirect('superuser:show_icos')

@never_cache
@login_and_user_type_required('S')
def reject_ico(request, ico_id):
    ico = get_object_or_404(ICOEntity, pk=ico_id)
    history = FarmerHistory.objects.filter(farmer=ico.farmer)

    if request.method == 'POST':
        form = ICORejectionForm(request.POST, instance=ico)
        if form.is_valid():
            ico.is_rejected = True
            form.save()
            ico_rejection_email.delay(ico.farmer.user.first_name, ico.farmer.user.email, ico.crop, ico.rejection_reason)
            return redirect('superuser:show_icos')
    else:
        form = ICORejectionForm(instance=ico)

    context = {
                'ico': ico,
                'history': history,
                'form': form,
                'errorModal': True,
                }
    return render(request, 'superuser/ico_detail.html', context)

@never_cache
def force_ico_returns(request, ico_id):
    ico = get_object_or_404(ICOEntity, pk=ico_id)

            
    farmer_balance = ico.farmer.wallet.balance
    total_quantity = ICOTransactions.objects.filter(ico_id=ico_id).aggregate(Sum('quantity'))['quantity__sum']
    
    investor_share = farmer_balance/total_quantity
    
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
            investor_forced_return_email.delay(investor_transaction.investor.user.first_name, investor_transaction.investor.user.email, transfer_amount, ico.crop, ico.farmer.user.first_name, investment_amount)
        
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
            revenue=farmer_balance,
            expenses=ico.capital
        )
    
    redirect_url = reverse('superuser:ico_details', kwargs={'ico_id': ico_id})
    return redirect(redirect_url)

# Farmer Related View here
@never_cache
@login_and_user_type_required('S')
def show_farmers(request):
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')

    farmers = Farmer.objects.all()
    # Filter based on the selected option
    if filter_type == 'not_verified':
        farmers = Farmer.objects.filter(
            is_verified=False,
            is_rejected=False,
        )

     # Apply search filter if search_query is present
    if search_query:
        farmers = farmers.filter(
            Q(user__first_name__icontains=search_query) | Q(user__last_name__icontains=search_query) | Q(user__username__icontains=search_query)
        )

    items_per_page = 5

    paginator = Paginator(farmers, items_per_page)
    page = request.GET.get('page')

    try:
        farmers = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, deliver the first page.
        farmers = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page.
        farmers = paginator.page(paginator.num_pages)
    
    context = {
        'farmers': farmers,
        'filter_type': filter_type,
    }
    return render(request, 'superuser/show_farmers.html', context)

@never_cache
@login_and_user_type_required('S')
def farmer_details(request, user_id):
    farmer = Farmer.objects.get(user__pk=user_id)
    history = FarmerHistory.objects.filter(farmer=farmer)
    form = FarmerRejectionForm(instance=farmer)
    context = {
        'farmer': farmer,
        'history': history,
        'form': form,
    }
    return render(request, 'superuser/farmer_detail.html', context)

@never_cache
@login_and_user_type_required('S')
def approve_farmer(request, user_id):
    farmer = Farmer.objects.get(user__pk=user_id)
    farmer.is_verified = True
    farmer.save()
    # print('came here', farmer.is_verified)
    # You can add additional logic or redirection here if needed
    farmer_verified_email.delay(farmer.user.first_name, farmer.user.email)
    return redirect('superuser:show_farmers')

@never_cache
@login_and_user_type_required('S')
def reject_farmer(request, user_id):
    farmer = Farmer.objects.get(user__pk=user_id)
    history = FarmerHistory.objects.filter(farmer=farmer)

    if request.method == 'POST':
        form = FarmerRejectionForm(request.POST, instance=farmer)
        if form.is_valid():
            farmer.is_rejected = True
            form.save()
            farmer_rejection_email.delay(farmer.user.first_name, farmer.user.email, farmer.rejection_reason)
            return redirect('superuser:show_farmers')
    else:
        form = FarmerRejectionForm(instance=farmer)

    context = {
                'farmer': farmer,
                'history': history,
                'form': form,
                'errorModal': True,
                }
    return render(request, 'superuser/farmer_detail.html', context)


# Investor Related View here
@never_cache
@login_and_user_type_required('S')
def show_investors(request):
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')

    investors = Investor.objects.all()
    # Filter based on the selected option
    if filter_type == 'not_verified':
        investors = Investor.objects.filter(
            is_verified=False,
            is_rejected=False,
        )

     # Apply search filter if search_query is present
    if search_query:
        investors = investors.filter(
            Q(user__first_name__icontains=search_query) | Q(user__last_name__icontains=search_query) | Q(user__username__icontains=search_query)
        )

    items_per_page = 5

    paginator = Paginator(investors, items_per_page)
    page = request.GET.get('page')

    try:
        investors = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, deliver the first page.
        investors = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page.
        investors = paginator.page(paginator.num_pages)

    context = {
        'investors': investors,
        'filter_type': filter_type,
    }
    return render(request, 'superuser/show_investors.html', context)

@never_cache
@login_and_user_type_required('S')
def investor_details(request, user_id):
    investor = Investor.objects.get(user__pk=user_id)
    form = InvestorRejectionForm(instance=investor)
    context = {
        'investor': investor,
        'form': form,
    }
    return render(request, 'superuser/investor_detail.html', context)

@never_cache
@login_and_user_type_required('S')
def approve_investor(request, user_id):
    investor = Investor.objects.get(user__pk=user_id)
    investor.is_verified = True
    investor.save()
    investor_verified_email.delay(investor.user.first_name, investor.user.email)
    return redirect('superuser:show_investors')

@never_cache
@login_and_user_type_required('S')
def reject_investor(request, user_id):
    investor = Investor.objects.get(user__pk=user_id)

    if request.method == 'POST':
        form = InvestorRejectionForm(request.POST ,instance=investor)
        if form.is_valid():
            investor.is_rejected = True
            form.save()
            investor_rejection_email.delay(investor.user.first_name, investor.user.email, investor.rejection_reason)
            return redirect('superuser:show_investors')
    else:
        form = InvestorRejectionForm(instance=investor)

    context = {
                'investor': investor,
                'form': form,
                'errorModal': True,
                }
    return render(request, 'superuser/investor_detail.html', context)