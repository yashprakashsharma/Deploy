from django.db import models
from farmer.models import ICOEntity
from core.models import Investor

# Create your models here.
class ICOTransactions(models.Model):
    ico = models.ForeignKey(ICOEntity, on_delete=models.CASCADE)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    per_entity_cost = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.pk} - {self.investor} ({self.quantity} units)"

    class Meta:
        verbose_name_plural = "ICO Transactions"