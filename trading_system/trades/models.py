from django.db import models
from django.contrib.auth.models import User

# Create models here that meet the project's needs.

# Stocks will have an id, name, and price.
# ID in Austtralian Stock Exchange consists of a 3-4 letters 
# but this will use the ISIN identifier which is 12 alphanumeric code.
class Stock(models.Model):
    id = models.CharField(max_length=12, primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

# Users with ability to place orders to buy and sell stocks
# uses the Django default model for user with authentication.
class Order(models.Model):
    BUY = 'buy'
    SELL = 'sell'
    ORDER_TYPES = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.stock} - {self.order_type} - {self.quantity}"
