from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from trades.models import Stock, Order
import os
import csv
from django.conf import settings

class Command(BaseCommand):
    help = 'Process bulk trade CSV files from a preconfigured directory'

    def handle(self, *args, **kwargs):
        bulk_trades_dir = settings.BULK_TRADES_DIR

        # Process each CSV file in the directory
        for filename in os.listdir(bulk_trades_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(bulk_trades_dir, filename)
                self.process_csv(file_path)
                self.stdout.write(self.style.SUCCESS(f'Successfully processed {filename}'))

    def process_csv(self, file_path):
        with open(file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                username, stock_id, order_type, quantity = row
                try:
                    user = User.objects.get(username=username)
                    stock = Stock.objects.get(id=stock_id)
                    Order.objects.create(
                        user=user,
                        stock=stock,
                        order_type=order_type,
                        quantity=int(quantity),
                        price=stock.price
                    )
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
                except Stock.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Stock {stock_id} does not exist'))
