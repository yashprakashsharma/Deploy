from django.contrib import admin
from core.models import CustomUser, Farmer, Investor, Wallet, OtpToken

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'phone', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'balance')
    search_fields = ('id',)  # Assuming you want to be able to search by Wallet ID

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('user', 'aadhar_number', 'pan_number', 'is_verified', 'land_area', 'wallet')
    search_fields = ('user__username', 'aadhar_number', 'pan_number')

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('user', 'aadhar_number', 'pan_number', 'is_verified', 'wallet')
    search_fields = ('user__username', 'aadhar_number', 'pan_number')

@admin.register(OtpToken)
class OtpTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'otp_created_at')
    search_fields = ('user__username', 'user__first_name')