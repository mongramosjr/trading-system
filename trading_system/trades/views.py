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
import logging

logger = logging.getLogger('trading_system_console_log')


# Create your views here.

# use the djangoerestframework viewsets
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        """
        Placing of order by users. When an order is placed, 
        record the quantity of the stock the user wants to buy or sell.

        Args:
            Order

        Returns:
            HTTP status code 201 or 400 or 404 if stock is non-existent
        """
        stock_id = request.data.get('stock')
        stock = get_object_or_404(Stock, id=stock_id)

        user = request.user

        # Instantiate the serializer with the request data
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Save the order, associating it with the current user and stock price
            serializer.save(user=user, price=stock.price)
            return Response({'stock': stock_id, 'user': user.get_username()}, status=status.HTTP_201_CREATED)
        else:
            # Return errors if the serializer is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
