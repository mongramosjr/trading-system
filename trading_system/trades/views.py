from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Stock, Order
from .serializers import StockSerializer, OrderSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404
import csv

# Create your views here.

# use the djangoerestframework viewsets
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def place_order(self, serializer):
        """
        Placing of order by users. When an order is placed, 
        Record the quantity of the stock the user wants to buy or sell
        Args:
            Order

        Returns:
            HTTP status code 201

        """
        stock = get_object_or_404(Stock, id=self.request.data['stock'])
        serializer.save(user=self.request.user, price=stock.price)

    @action(detail=False, methods=['post'], parser_classes=[FileUploadParser])
    def bulk_trade(self, request):
        """
        Accepts a CSV upload to place trades in bulk.

        Args:
            file

        Returns:
            HTTP status code 201
        """
        file_obj = request.data['file']
        csv_reader = csv.reader(file_obj.read().decode('utf-8').splitlines())
        for row in csv_reader:
            user = User.objects.get(username=row[0])
            stock = Stock.objects.get(id=row[1])
            Order.objects.create(
                user=user,
                stock=stock,
                order_type=row[2],
                quantity=row[3],
                price=stock.price
            )
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def total_investment(self, request):
        """
        Retrieval of the total value invested in a single stock by a user. 
        To calculate this - we need to sum all the value of all orders placed by the user for a single stock. 
        Order value is calculated by multiplying quantity and stock price.

        Args:
            user credential and stock id 

        Returns:
            stock id and the total value.
        """
        user = request.user
        stock_id = request.query_params.get('stock_id')
        stock = get_object_or_404(Stock, id=stock_id)
        total_value = Order.objects.filter(user=user, stock=stock).aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total']
        return Response({'stock_id': stock_id,'total_value': total_value}, status=status.HTTP_200_OK)
