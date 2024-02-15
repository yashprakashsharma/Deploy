from django.db import models
from django.utils import timezone
from core.models import Farmer
from datetime import timedelta
# Create your models here.

class FarmerHistory(models.Model):
    SEASON_CHOICES = [
        ('Rabi', 'Rabi'),
        ('Kharif', 'Kharif'),
    ]

    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    season = models.CharField(max_length=6, choices=SEASON_CHOICES)
    year = models.IntegerField()
    crop = models.CharField(max_length=20)
    area_cultivated = models.FloatField()
    revenue = models.FloatField()
    expenses = models.FloatField()

    @property
    def percentage(self):
        # Calculate profit or loss percentage
        if self.revenue > self.expenses:
            return ((self.revenue - self.expenses) / self.expenses) * 100
        elif self.revenue < self.expenses:
            return -(((self.expenses - self.revenue) / self.expenses) * 100)
        else:
            return 0

    def __str__(self):
        return f"{self.farmer.user.username}'s History of {self.season}, {self.year}"


class ICOEntity(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    isVerified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_return_provided = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    crop = models.CharField(max_length=20)
    land_area = models.FloatField()
    capital = models.FloatField()
    quantity = models.IntegerField()
    sold_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    closes_on = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField()

    @property
    def verified_and_active_entities(self):
        current_datetime = timezone.now()
        return ICOEntity.objects.filter(
            isVerified=True,
            closes_on__gte=current_datetime,
            sold_quantity__lt=models.F('quantity')
        ).order_by('closes_on')
    
    @property
    def stock_available(self):
        return self.quantity-self.sold_quantity
    
    @property
    def price(self):
        return float(self.capital)/float(self.quantity)
    
    @property
    def status(self):
        current_datetime = timezone.now()

        if not self.isVerified:
            return "Not Verified"
        elif current_datetime < self.closes_on:
            return "Open"
        elif current_datetime > self.return_date:
            return "Closed"
        elif self.closes_on <= current_datetime <= self.return_date:
            return "Pending"
        
    @property
    def open_return(self):
        current_datetime = timezone.now()
        return self.isVerified and current_datetime >= (self.return_date - timedelta(days=10))  and self.is_return_provided == False

    @property
    def is_remaining(self):
        current_datetime = timezone.now()
        return self.isVerified and current_datetime >= (self.return_date + timedelta(days=10))  and self.is_return_provided == False

    def __str__(self):
        return f"{self.farmer.user.username}'s ICOEntity - {self.crop}"