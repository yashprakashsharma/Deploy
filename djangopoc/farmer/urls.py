from django.urls import path
from .views import home_farmer, notverified_farmer, farmer_profile, farmer_wallet, deposit_money, add_farmer_history, edit_farmer_history, add_ico_entity, ICOListView, ico_details_view, edit_ico_entity, FarmerEditView, ico_returns

app_name = 'farmer'

urlpatterns = [
    path('', home_farmer, name='home_farmer'),
    path('notverified', notverified_farmer, name='notverified_farmer'),
    path('profile/', farmer_profile, name='farmer_profile'),
    path('wallet/', farmer_wallet, name='farmer_wallet'),
    path('wallet_deposit/', deposit_money, name='deposit_money'),
    path('add_farmer_history/', add_farmer_history, name='add_farmer_history'),
    path('edit_farmer_history/<int:history_id>/', edit_farmer_history, name='edit_farmer_history'),
    path('add_ico_entity/', add_ico_entity, name='add_ico_entity'),
    path('show_farmer_icos/', ICOListView.as_view(), name='show_farmer_icos'),
    path('ico_details/<int:ico_id>/', ico_details_view, name='ico_details'),
    path('edit_ico_entity/<int:ico_id>/', edit_ico_entity, name='edit_ico_entity'),
    path('edit_farmer/', FarmerEditView.as_view(), name='edit_farmer'),
    path('ico_returns/<int:ico_id>/', ico_returns, name='ico_returns'),
    # Add other URL patterns as needed
]