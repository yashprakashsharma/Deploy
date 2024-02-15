from django.contrib import admin
from investor.models import ICOTransactions

# Register your models here.
@admin.register(ICOTransactions)
class ICOTransactionsAdmin(admin.ModelAdmin):
    list_display = ('ico', 'investor', 'quantity', 'per_entity_cost', 'updated_at')
    list_filter = ('ico', 'investor')
    search_fields = ('quantity', 'investor__user__username')  # Assuming there's a 'user' field in the 'Farmer' model
    # Add any other configurations or customizations as needed