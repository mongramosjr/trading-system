# trading-system
Simple trading system

*trades_order* and *trades_stocks* are just the two database tables for this project plus the required tables of Django

## 1. Create an env for Python 3.x
I used 3.10.13 in this project.

```bash
python -m venv <environment_name>
source <environment_name>/bin/activate
```

## 2. Download the git and go to the Django project folder trading-system

```bash
git clone https://github.com/mongramosjr/trading-system.git
cd trading-system
```

## 3. Setup needed Python packages
First, install Django and Django REST Framework

```bash
pip install -r requirements
```

Then go to the main directory of Django project
```bash
cd trading_system
```

## 4. Run migrations.

```bash
python manage.py makemigrations
python manage.py migrate
```

## 5. Populate the stock models or update it in admin page
```bash
python manage.py update_stocks
```

Verify that the stock data is populated and updated correctly via admin interface or checking the sqlite3 database.

## 6. Schedule the Command Using Cron Job
Open the crontab editor:

```bash
crontab -e
```

```python
0 0 * * * /path/to/your/virtualenv/bin/python /path/to/your/project/manage.py python manage.py parse_csv path/to/your/data.csv

0 0 * * * /path/to/your/virtualenv/bin/python /path/to/your/project/manage.py python manage.py process_bulk_trades 

0 0 * * * /path/to/your/virtualenv/bin/python /path/to/your/project/manage.py update_stocks
```

## 7. Unit Testing
Run the tests using Django's test runner

```bash
python manage.py test trades
```

There are three tests in the *trading_system/trades/tests.py*

* *test_place_order*: Tests if an order can be placed successfully.
* *test_bulk_trade*: Tests bulk uploading of orders via a CSV file.
* *test_total_investment*: Tests retrieving the total value invested in a single stock by a user.

## 8. Running the API Endpoints
Start the server with
```bash
python manage.py runserver
```
## 9. Testing the API Endpoints
To test all the API endpoints using the terminal, use the tool curl.
But first you need to create an admin user to easily manage authentication and permissions.

```bash
python manage.py createsuperuser
```

Also create a regular user to test the API endpoints

```bash
python manage.py create_user username email@example.com password
```


(1) Place an Order
```bash
curl -X POST http://127.0.0.1:8000/api/orders/place_order/ \
     -H "Content-Type: application/json" \
     -d '{
           "stock": "MSFT",
           "order_type": "buy",
           "quantity": 10
         }' \
     -u username:password
```

(2) Bulk Trading
```bash
curl -X POST http://127.0.0.1:8000/api/orders/bulk_trade/ \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/file.csv" \
     -u username:password
```

Ensure the csv file has this format [username,stock_id,buy_or_sell,amount]
```python
username,TSLA,buy,10
username,RAMOS,sell,5
username,GOOGL,sell,5
```

(3) Retrieval of Total Investment
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/total_investment/?stock=AAPL" \
     -u username:password
```