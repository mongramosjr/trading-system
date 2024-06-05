from django.contrib import admin
from .models import Stock, Order

# Register your models here.

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'order_type', 'quantity', 'price', 'timestamp')

