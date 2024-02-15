from django.urls import path
from .views import SignUpView, LoginView, LogoutView, home, home2, index, FarmerRegistrationView, InvestorRegistrationView, verify_email, resend_otp
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path("verify-email/<str:username>", verify_email, name="verify-email"),
    path("resend-otp", resend_otp, name="resend-otp"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register_farmer/', FarmerRegistrationView.as_view(), name='register_farmer'),
    path('register_investor/', InvestorRegistrationView.as_view(), name='register_investor'),
    path('home/', home, name='home'),
    path('home2/', home2, name='home2'),
    # Add other URL patterns as needed
]