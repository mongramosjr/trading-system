from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from trades.models import Stock, Order
import os
import csv
from django.conf import settings

class Command(BaseCommand):
    help = 'Process a bulk trade CSV file from a preconfigured directory'

    argument_name = 'filename'
    argument_description = 'Path to the CSV file containing bulk trades'

    def add_arguments(self, parser):
        parser.add_argument(self.argument_name, nargs=1, type=str, help=self.argument_description)


    def handle(self, *args, **kwargs):
        filename = kwargs.get(self.argument_name)[0]  # Access the first element from the argument list
        bulk_trades_dir = settings.BULK_TRADES_DIR

        file_path = os.path.join(bulk_trades_dir, filename)
        self.process_csv(file_path)
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {filename}'))
        
    def process_csv(self, file_path):
        with open(file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                username, stock_id, order_type, quantity = row
                # skip at header
                if username == 'user': continue
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
