from django.urls import path
from .views import home_investor, notverified_investor, investor_profile, investor_wallet, deposit_money, InvestorICOListView, buy_ico, investor_icos, ico_details, InvestorEditView

app_name = 'investor'

urlpatterns = [
    path('', home_investor, name='home_investor'),
    path('notverified', notverified_investor, name='notverified_investor'),
    path('profile/', investor_profile, name='investor_profile'),
    path('wallet/', investor_wallet, name='investor_wallet'),
    path('wallet_deposit/', deposit_money, name='deposit_money'),
    path('show_icos/', InvestorICOListView.as_view(), name='show_icos'),
    path('buy_ico/<int:ico_id>/', buy_ico, name='buy_ico'),
    path('investor_icos/', investor_icos, name='investor_icos'),
    path('ico_details/<int:ico_id>/', ico_details, name='ico_details'),
    path('edit_investor/', InvestorEditView.as_view(), name='edit_investor'),
    # Add other URL patterns as needed
]