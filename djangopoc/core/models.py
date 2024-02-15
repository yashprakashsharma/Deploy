from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.conf import settings
import secrets

# alidators here
ext_validator = FileExtensionValidator(['pdf'])

# Create your models here.
class CustomUser(AbstractUser):
    USER_TYPES = (
        ('F', 'Farmer'),
        ('I', 'Investor'),
        ('S', 'SuperUser'),
    )
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    username = models.CharField(max_length=150, unique=True, blank=False)
    user_type = models.CharField(max_length=1, choices=USER_TYPES, default='I')
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=True, default="NA")
    phone = models.CharField(max_length=10, unique=True, blank=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name" ,"username", "phone"]

    def __str__(self):
        return self.username
    
class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Wallet(models.Model):
    balance = models.FloatField(default=0.0)
    def deposit(self, amount):
        self.balance += amount
        self.save()
    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False
    
class Farmer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    aadhar_number = models.CharField(max_length=12, unique=True,blank=False)
    pan_number = models.CharField(max_length=10, unique=True, blank=False)
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    land_area = models.FloatField(default=0.0)
    documents = models.FileField(upload_to='farmer_documents/', validators=[ext_validator], null=True, default=None)
    wallet = models.ForeignKey(Wallet, related_name="wallet_farmer", on_delete=models.CASCADE, null=True)


    

class Investor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    aadhar_number = models.CharField(max_length=12, unique=True,blank=False)
    pan_number = models.CharField(max_length=10, unique=True, blank=False)
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    documents = models.FileField(upload_to='investor_documents/', validators=[ext_validator], null=True, default=None)
    wallet = models.ForeignKey(Wallet, related_name="wallet_investor", on_delete=models.CASCADE, null=True)