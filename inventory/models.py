from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Ingredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # ex Flour, sugar, etc
    quantity = models.FloatField()
    unit = models.CharField(max_length=20) # ex grams, cups, tbsp, etc
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    expiration_date = models.DateField(null=True, blank=True)
    low_stock_threshold = models.FloatField(default=0) # when to report low stock
    updated_at = models.DateTimeField(auto_now=True) # track last time ingredient was edited

    # to display object nicely
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
