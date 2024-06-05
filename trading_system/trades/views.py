from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Stock, Order
from .serializers import StockSerializer, OrderSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404
import csv
import logging, copy

logger = logging.getLogger('django')


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
            quantity, order_type, stock

        Returns:
            error message or {'stock': stock, 'price': price, 'amount':amount}
            HTTP status code 201 or 400 or 404 if stock is non-existent
        """
        quantity = request.data.get('quantity')
        order_type = request.data.get('order_type')
        stock_id = request.data.get('stock')
        stock = get_object_or_404(Stock, id=stock_id)
        amount = float(quantity)*float(stock.price)
        user = request.user
        price = stock.price

        logger.debug(f'Processing request data {repr(request.data)} from {repr(request.user)} ')
        # NOTE: serializer always returns below error, it couldn't get the value from auth 
        # {"price":["This field is required.", "user": "This field is required."]
        request_data = copy.deepcopy(request.data)

        # if price key is not included in the request data
        if 'price' not in request_data:
            request_data["price"] = stock.price
        else:
            price = request_data["price"]

        # get the pk of the user
        user_db = User.objects.get(username=request.user.username)
        request_data["user"] = user_db.id

        # Instantiate the serializer with the request data
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid():
            # Save the order, associating it with the current user and stock price
            serializer.save(user=user)
            return Response({'stock': stock_id, 'price': price, 'amount':amount}, 
                            status=status.HTTP_201_CREATED)
        else:
            # Return errors if the serializer is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def bulk_trade(self, request):
        """
        Accepts a CSV upload to place trades in bulk.

        Args:
            file

        Returns:
            HTTP status code 201
        """
        file_obj = request.data['file']
        csv_reader = csv.DictReader(file_obj.read().decode('utf-8').splitlines())
        user = request.user

        logger.debug(f'Processing request from {repr(request.user)} ')
        
        for row in csv_reader:
            logger.debug(f'Processing csv {repr(row)} ')

            user = User.objects.get(username=row['user'])
            stock = get_object_or_404(Stock, id=row['stock'])
            
            Order.objects.create(
                user=user,
                stock=stock,
                order_type=row['order_type'],
                quantity=row['quantity'],
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
            user credential and stock

        Returns:
            error message or {'stock': stock, 'total_value': total_value}
            HTTP status code 200
        """
        user = request.user
        stock_id = request.query_params.get('stock')
        stock = get_object_or_404(Stock, id=stock_id)
        total_value = Order.objects.filter(user=user, stock=stock).aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total']
        return Response({'stock': stock_id,'total_value': total_value}, status=status.HTTP_200_OK)
