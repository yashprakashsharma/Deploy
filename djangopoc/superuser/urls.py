from django.urls import path
from superuser.views import home_superuser, show_icos, superuser_profile, ico_details, approve_ico, reject_ico, show_farmers, farmer_details, approve_farmer, reject_farmer, show_investors, investor_details, approve_investor, reject_investor, force_ico_returns

app_name = 'superuser'

urlpatterns = [
    path('', home_superuser, name='home_superuser'),
    path('profile/', superuser_profile, name='superuser_profile'),
    path('show_icos/', show_icos, name='show_icos'),
    path('ico_details/<int:ico_id>/', ico_details, name='ico_details'),
    path('approve_ico/<int:ico_id>/', approve_ico, name='approve_ico'),
    path('reject_ico/<int:ico_id>/', reject_ico, name='reject_ico'),
    path('force_ico_returns/<int:ico_id>/', force_ico_returns, name='force_ico_returns'),
    path('show_farmers/', show_farmers, name='show_farmers'),
    path('farmer_details/<int:user_id>/', farmer_details, name='farmer_details'),
    path('approve_farmer/<int:user_id>/', approve_farmer, name='approve_farmer'),
    path('reject_farmer/<int:user_id>/', reject_farmer, name='reject_farmer'),
    path('show_investors/', show_investors, name='show_investors'),
    path('investor_details/<int:user_id>/', investor_details, name='investor_details'),
    path('approve_investor/<int:user_id>/', approve_investor, name='approve_investor'),
    path('reject_investor/<int:user_id>/', reject_investor, name='reject_investor'),
]