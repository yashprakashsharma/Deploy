from django.contrib import admin
from farmer.models import FarmerHistory, ICOEntity

# Register your models here.
# Farmer History model
@admin.register(FarmerHistory)
class FarmerHistoryAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'season', 'year', 'crop', 'area_cultivated', 'revenue', 'expenses')
    list_filter = ('season', 'year')
    search_fields = ('crop', 'farmer__user__username')  # Assuming there's a 'user' field in the 'Farmer' model
    # Add any other configurations or customizations as needed

@admin.register(ICOEntity)
class ICOEntityAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'isVerified', 'crop', 'land_area', 'capital', 'quantity', 'sold_quantity', 'created_at', 'closes_on', 'return_date')
    list_filter = ('isVerified', 'closes_on')
    search_fields = ('crop', 'farmer__user__username')  # Assuming there's a 'user' field in the 'Farmer' model