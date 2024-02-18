from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from .forms import CustomUserCreationForm, LoginForm, FarmerRegistrationForm, InvestorRegistrationForm
from .models import Farmer, Investor, Wallet, OtpToken
from .decorators import login_and_farmer_required, login_and_investor_required, login_and_user_type_required
import secrets

class SignUpView(View):
    template_name = 'core/signup.html'

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("verify-email", username = request.POST['username'])
            # return redirect('login')  # Redirect to the login page after successful registration
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'core/login.html'  # Adjust the template path accordingly

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Check user type and related model instance
                if user.user_type == 'F':
                    farmer_instance = Farmer.objects.filter(user=user).first()
                    if farmer_instance:
                        return redirect('farmer:home_farmer')  # Redirect to farmer home page for registered Farmers
                    else:
                        return redirect('register_farmer')  # Redirect to register_farmer if not registered

                elif user.user_type == 'I':
                    investor_instance = Investor.objects.filter(user=user).first()
                    if investor_instance:
                        return redirect('investor:home_investor')
                    else:
                        return redirect('register_investor') # Redirect to register_investor if not registered
                    
                elif user.user_type == 'S':
                    return redirect('superuser:home_superuser')
                    
                return redirect('home')  # Redirect to the home page after successful login
            else:
                # Handle invalid login credentials
                messages.error(request, 'Invalid username or password.')
        return render(request, self.template_name, {'form': form})
    

@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    def get(self, request):
        logout(request)
        # Redirect to the desired page after logout
        return redirect('login')  # Replace 'login' with the actual name of your login URL pattern
    
class FarmerRegistrationView(View):
    template_name = 'core/register_farmer.html'

    # @method_decorator(login_required(login_url='login'))
    @method_decorator(login_and_user_type_required('F'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = FarmerRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = FarmerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Assuming your form includes necessary fields for farmer registration
            aadhar_number = form.cleaned_data['aadhar_number']
            pan_number = form.cleaned_data['pan_number']
            land_area = form.cleaned_data['land_area']
            documents = form.cleaned_data['documents']

            # Create a wallet for the farmer
            wallet_instance = Wallet.objects.create()

            farmer_instance = Farmer.objects.create(
                user=request.user,
                aadhar_number=aadhar_number,
                pan_number=pan_number,
                land_area=land_area,
                wallet=wallet_instance,
                documents=documents
            )

            return redirect('farmer:home_farmer')  # Redirect to Farmer home page after successful registration

        return render(request, self.template_name, {'form': form})
    
class InvestorRegistrationView(View):
    template_name = 'core/register_investor.html'

    # @method_decorator(login_required(login_url='login'))
    @method_decorator(login_and_user_type_required('I'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = InvestorRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = InvestorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Assuming your form includes necessary fields for farmer registration
            aadhar_number = form.cleaned_data['aadhar_number']
            pan_number = form.cleaned_data['pan_number']
            documents = form.cleaned_data['documents']
            
            # Create a wallet for the investor
            wallet_instance = Wallet.objects.create()

            investor_instance = Investor.objects.create(
                user=request.user,
                aadhar_number=aadhar_number,
                pan_number=pan_number,
                wallet=wallet_instance,
                documents=documents
            )

            return redirect('investor:home_investor')  # Redirect to home page after successful registration

        return render(request, self.template_name, {'form': form})
    
@login_and_farmer_required
def home(request):
    return HttpResponse('THis is home for farmer')

@login_and_investor_required
def home2(request):
    print('in investor home', request.user)
    return HttpResponse('This is home for investor')

def index(request):
    return render(request, 'core/index.html')

def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    print('recieved username: ', username)
    user_otp = OtpToken.objects.filter(user=user).last()
    if request.method == 'POST':
        if user_otp.otp_code == request.POST['otp_code']:

            #valid token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True
                user.save()
                return redirect('login')
            
            # expired token
            else:
                print('timeout')
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("verify-email", username=user.username)
            
        # invalid otp code
        else:
            print('wring')
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("verify-email", username=user.username)
    
    return render(request, 'core/verify_token.html')

def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]
        
        if get_user_model().objects.filter(email=user_email).exists():
            otp_code = secrets.token_hex(3)
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_code=otp_code, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            
            
            # email variables
            subject="Email Verification"
            message = f"""
                                Hi {user.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{user.username}
                                
                                """
            sender = settings.EMAIL_HOST_USER
            receiver = [user.email, ]
        
        
            # send email
            send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=True,
                )
            
            return redirect("verify-email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("resend-otp")
        
    return render(request, 'core/resend_otp.html')
