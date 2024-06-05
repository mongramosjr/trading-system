from django.core.management.base import BaseCommand
from trades.models import Stock
import yfinance as yf
import time
import random

class Command(BaseCommand):
    help = 'Updates the stock data from yfinance'

    def handle(self, *args, **kwargs):
        # List of stock tickers to track
        stock_symbols = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
        
        # For testing
        #stock_symbols = ['MONG', 'RAMOS']
        
        #stock_data = yf.download(tickers=stock_symbols, period="1d")["Close"]
        #print(stock_data)
        #exit

        # Update stock data for each ticker
        for ticker in stock_symbols:
            stock_data = yf.Ticker(ticker)
            try:
                # Check if data is available before accessing attributes
                if not stock_data.info:
                    self.stdout.write(self.style.WARNING(f"Error: No data available for {ticker}"))
                    continue

                #print(stock_data.info)

                # Get the current price and the name 
                price = stock_data.info['currentPrice']
                name = stock_data.info['shortName']
                
                # Update or create objects in the database
                stock, created = Stock.objects.update_or_create(
                    id=ticker,
                    defaults={
                        'name': name,
                        'price': price
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully added stock {ticker}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated stock {ticker}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating {ticker}: {e}"))
