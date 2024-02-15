from functools import wraps
from django.shortcuts import redirect
from .models import Farmer, Investor

def login_and_farmer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if the user is not authenticated

        farmer_instance = Farmer.objects.filter(user=request.user).first()
        if not farmer_instance:
            return redirect('register_farmer')  # Redirect to register_farmer if Farmer instance does not exist

        return view_func(request, *args, **kwargs)

    return _wrapped_view

def login_and_investor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if the user is not authenticated

        investor_instance = Investor.objects.filter(user=request.user).first()
        if not investor_instance:
            return redirect('register_investor')  # Redirect to register_investor if Investor instance does not exist

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def login_and_user_type_required(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # Redirect to login if the user is not authenticated

            if request.user.user_type != user_type:
                return redirect('index')  # Redirect to home page if user_type is not the expected type

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def farmer_verified(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if the user is not authenticated

        farmer_instance = Farmer.objects.filter(user=request.user).first()
        if not farmer_instance:
            return redirect('register_farmer')  # Redirect to register_farmer if Farmer instance does not exist
        
        if not farmer_instance.is_verified:
            return redirect('farmer:notverified_farmer')

        return view_func(request, *args, **kwargs)

    return _wrapped_view

def investor_verified(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if the user is not authenticated

        investor_instance = Investor.objects.filter(user=request.user).first()
        if not investor_instance:
            return redirect('register_investor')  # Redirect to register_investor if Investor instance does not exist
        
        if not investor_instance.is_verified:
            return redirect('investor:notverified_investor')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
