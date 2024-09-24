import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)


# Function to generate random timestamps
def random_timestamp(start, end, n):
    return [start + timedelta(seconds=random.randint(0, int((end - start).total_seconds()))) for _ in range(n)]


# Define ranges for each case
ranges = [
    (1000, 100000),  # Range 1
    (50000, 500000),  # Range 2
    (1000, 10000),  # Range 3
    (50000, 900000),  # Range 4
]

# Generate sample data
data = []
start_time = datetime(2024, 9, 21, 0, 0, 0)
end_time = datetime(2024, 9, 21, 23, 59, 59)

# Combinations of event_source and identifier for each range
combinations = [
    ('A', 'X'),
    ('B', 'Y'),
    ('C', 'Z'),
    ('D', 'W')
]

# 1. Generate 1000 entries for each price range
for i, price_range in enumerate(ranges):
    event_source, identifier = combinations[i]
    prices = np.random.randint(price_range[0], price_range[1], 10000).tolist()  # Convert to native Python int
    timestamps = random_timestamp(start_time, end_time, 10000)

    for j in range(10000):
        data.append({
            'event_type': 'Trade',
            'event_source': event_source,
            'identifier': identifier,
            'timestamp': timestamps[j].isoformat() + 'Z',  # Add 'Z' for UTC time format
            'data': {
                'price': int(prices[j])  # Ensure price is a Python int
            }
        })

# 2. Generate 5 outliers for each combination (outside normal price ranges)
outlier_ranges = [
    (1000000, 2000000),  # Outliers for range 1
    (1000, 2000),  # Outliers for range 2
    (400000, 500000),  # Outliers for range 3
    (0, 2000),  # Outliers for range 4
]

# Add 5 outliers for each combination
for i, outlier_range in enumerate(outlier_ranges):
    event_source, identifier = combinations[i]
    outlier_prices = np.random.randint(outlier_range[0], outlier_range[1], 5).tolist()  # Convert to native Python int
    outlier_timestamps = random_timestamp(start_time, end_time, 5)

    for j in range(5):
        data.append({
            'event_type': 'Trade',
            'event_source': event_source,
            'identifier': identifier,
            'timestamp': outlier_timestamps[j].isoformat() + 'Z',  # Add 'Z' for UTC time format
            'data': {
                'price': int(outlier_prices[j])  # Ensure price is a Python int
            }
        })

# Export data to JSON
with open('sample_trade_data.json', 'w') as f:
    json.dump(data, f, indent=4, default=str)  # Convert objects to string where needed