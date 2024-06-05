# trading-system
Simple trading system

*trades_order* and *trades_stocks* are just the two database tables for this project plus the required tables of Django

## 1. Create an env for Python 3.x
I used Python 3.10.13 in this project.

Note: Use Python version 3.3 and above.

```bash
python -m venv <environment_name>
source <environment_name>/bin/activate
```

## 2. Download the git and go to the project folder *git_folder*

```bash
git clone https://github.com/mongramosjr/trading-system.git git_folder
cd git_folder
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

Verify that the stock data is populated and updated correctly via admin interface (see steps #9 on creating super user) or checking the sqlite3 database. sqlite3 database is located in the main folder of Django project, named *db.sqlite3*

## 6. Schedule the Command Using Cron Job

Two cron jobs are configured to process CSV files in the bulk_trades directory located at /path/to/your/git_project/trading_system and place bulk trades.

* *parse_csv*: This cron job focuses on a single CSV file within the directory. It parses the data in the file and uses the information to initiate trades in bulk. There is an existing csv file named *bulk_trades.csv*. You may place your own csv file at bulk_trades directory and ensure it follows the following format, first row is the header.

```python
user,stock,order_type,quantity
username,TSLA,buy,10
othername,RAMOS,sell,5
somename,GOOGL,sell,46
```

* *process_bulk_trades*: This cron job handles multiple CSV files located in the same directory. It iterates through each file, parses its data, and uses the information to execute bulk trades.

A dedicated cron job keeps stock prices up-to-date, it is *update_stocks*. This job retrieves the latest prices for all tracked stocks.

Open the crontab editor:

```bash
crontab -e
```

```python
0 0 * * * /path/to/your/environment_name/bin/python /path/to/your/git_project/trading_system/manage.py python manage.py parse_csv bulk_trades.csv

0 0 * * * /path/to/your/environment_name/bin/python /path/to/your/git_project/trading_system/manage.py python manage.py process_bulk_trades 

0 0 * * * /path/to/your/environment_name/bin/python /path/to/your/git_project/trading_system/manage.py update_stocks
```

## 7. Unit Testing
There are three tests in the *trading_system/trades/tests.py*

* *test_place_order*: Tests if an order can be placed successfully.
* *test_bulk_trade*: Tests bulk uploading of orders via a CSV file.
* *test_total_investment*: Tests retrieving the total value invested in a single stock by a user.

Run the tests using Django's test runner

```bash
python manage.py test trades
```

## 8. Running the API Endpoints
Start the server with
```bash
python manage.py runserver
```
## 9. Testing the API Endpoints
To test all the API endpoints using the terminal, use the commandline tool *curl*.
But first you need to create an admin user to easily manage authentication and permissions.

```bash
python manage.py createsuperuser
```

Also create a regular user to test the API endpoints or create regular user in admin UI.

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
     -H "Content-Disposition: attachment; filename=file.csv" \
     -F "file=@/path/to/your/file.csv" \
     -u username:password
```

Ensure the csv file has this format and header [user,stock,order_type,quantity]
```python
user,stock,order_type,quantity
username,TSLA,buy,10
username,RAMOS,sell,5
username,GOOGL,sell,46
username,MONG,buy,27
```

(3) Retrieval of Total Investment
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/total_investment/?stock=AAPL" \
     -u username:password
```