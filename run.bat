@echo off

:: Uncomment the following lines for concurrent execution
echo Running Python files concurrently...
start python run_customer.py
start python run_inventory.py
start python run_sale.py
start python run_admin.py
start python run_favorite.py
start python run_log.py
start python run_review.py

echo All scripts executed.
pause
