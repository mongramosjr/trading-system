from django.test import TestCase
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Stock, Order
from django.contrib.auth.models import User
import io
import csv


# Create your tests here.
class TradesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.stock = Stock.objects.create(id='MONG', name='Mong Ramos Jr. Inc.', price=120.00)
        self.order_data = {
            'user': self.user.id,
            'stock': self.stock.id,
            'order_type': 'buy',
            'quantity': 10,
            'price': 150.00,
        }


    def test_place_order(self):
        response = self.client.post(reverse('order-place-order'), self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.stock, self.stock)
        self.assertEqual(order.quantity, 10)


    def test_total_investment(self):
        Order.objects.create(user=self.user, stock=self.stock, order_type='buy', quantity=10, price=150.00)
        response = self.client.get(reverse('order-total-investment'), {'stock': self.stock.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_value'], 1500.00)

    
    def test_bulk_trade(self):
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow([self.user.username, self.stock.id, 'buy', 20])
        csv_file.seek(0)
        print(csv_file)
        response = self.client.post(
            reverse('order-bulk-trade'), 
            {'file': csv_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.stock, self.stock)
        self.assertEqual(order.quantity, 20)
