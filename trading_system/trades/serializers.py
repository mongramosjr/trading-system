from rest_framework import serializers
from .models import Stock, Order

# Serializer the Stock and Order models as requierement for REST api
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
