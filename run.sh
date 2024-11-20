#!/bin/bash

# Uncomment the following block for concurrent execution
echo "Running Python files concurrently..."
python3 run_customer.py &
python3 run_inventory.py 
wait  # Wait for all background processes to complete

echo "All scripts executed."
