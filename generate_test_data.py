#!/usr/bin/env python3
import random
import string
import requests
from datetime import datetime, timedelta
import socket
import argparse
from multiprocessing import Pool, Manager
from tqdm import tqdm

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_ip():
    return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"

def random_hostname():
    return f"test-{random_string(5)}.example.com"

def create_entry(args):
    i, total = args
    base_url = "http://127.0.0.1:8000"
    
    # Generate random data
    content = random_string(random.randint(5, 50))
    
    # Create the entry
    data = {
        "store": content
    }
    
    # Send the request
    try:
        response = requests.put(f"{base_url}/clipboard", json=data)
        if response.status_code == 200:
            return True, f"Created entry {i+1}/{total}: {content}"
        else:
            return False, f"Failed to create entry {i+1}: {response.text}"
    except Exception as e:
        return False, f"Error creating entry {i+1}: {str(e)}"

def generate_test_data(num_entries, num_processes=4):
    # Create a pool of workers
    with Pool(processes=num_processes) as pool:
        # Create arguments for each entry
        args = [(i, num_entries) for i in range(num_entries)]
        
        # Process entries in parallel with progress bar
        results = list(tqdm(
            pool.imap(create_entry, args),
            total=num_entries,
            desc="Generating entries"
        ))
        
        # Print any errors
        for success, message in results:
            if not success:
                print(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate test data for clipboard API')
    parser.add_argument('num_entries', type=int, help='Number of entries to generate')
    parser.add_argument('--processes', type=int, default=12, help='Number of processes to use (default: 4)')
    args = parser.parse_args()
    
    generate_test_data(args.num_entries, args.processes)
