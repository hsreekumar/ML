import random
import json
from datetime import datetime, timedelta


# Function to generate a random timestamp around a specific hour and minute
def generate_random_timestamp(base_time, day_offset):
    random_minutes = random.randint(-5, 5)
    timestamp = base_time + timedelta(days=day_offset, minutes=random_minutes)
    return timestamp.isoformat(timespec='milliseconds') + 'Z'


# Function to generate a completely random timestamp within a weekday
def generate_random_time_of_day(day_offset):
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)
    base_time = datetime.utcnow().replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    timestamp = base_time + timedelta(days=day_offset)
    return timestamp.isoformat(timespec='milliseconds') + 'Z'


# Function to check if a date is a weekday
def is_weekday(date):
    return date.weekday() < 5  # 0-4 are Monday to Friday


# Function to generate events
def generate_events(event_type, event_source, identifier, base_times, num_days=9500):
    events = []
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    for day_offset in range(num_days):
        current_date = today + timedelta(days=-day_offset)
        if is_weekday(current_date):  # Only generate events on weekdays
            for base_time in base_times:
                timestamp = generate_random_timestamp(
                    current_date + timedelta(hours=base_time['hour']), 0)
                event = {
                    'event_type': event_type,
                    'event_source': event_source,
                    'identifier': identifier,
                    'timestamp': timestamp
                }
                events.append(event)

    return events


# Function to generate outlier events at random times of the day
def generate_outlier_events(event_type, event_source, identifier, num_outliers, num_days=5):
    events = []
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    for day_offset in range(num_days):
        current_date = today + timedelta(days=-day_offset)
        if is_weekday(current_date):  # Only generate outlier events on weekdays
            for _ in range(num_outliers // num_days):  # Distribute the outliers evenly over days
                timestamp = generate_random_time_of_day(-day_offset)
                event = {
                    'event_type': event_type,
                    'event_source': event_source,
                    'identifier': identifier,
                    'timestamp': timestamp
                }
                events.append(event)

    return events


# Generate event sets
event_type_A = 'A'

# First set of events for the past 95 days, around 11 AM and 4 PM
base_times_11AM_4PM = [{'hour': 11}, {'hour': 16}]
events_1 = generate_events(event_type_A, 'B', 'C', base_times_11AM_4PM)

# Second set with different event_source and identifier, around 10 AM and 6 PM
events_2 = generate_events(event_type_A, 'D', 'E', [{'hour': 10}, {'hour': 18}])

# Third set with different event_source and identifier, around 5 AM and 10 PM
events_3 = generate_events(event_type_A, 'F', 'G', [{'hour': 5}, {'hour': 22}])

# Fourth set around 6 AM and 7 PM
events_4 = generate_events(event_type_A, 'H', 'I', [{'hour': 6}, {'hour': 19}])

# Fifth set around 6:30 PM alone
events_5 = generate_events(event_type_A, 'J', 'K', [{'hour': 18, 'minute': 30}])

# Add 10 random outlier events for event sets 1 to 4, and 5 outlier events for event set 5
outliers_1 = generate_outlier_events(event_type_A, 'B', 'C', 50)
outliers_2 = generate_outlier_events(event_type_A, 'D', 'E', 50)
outliers_3 = generate_outlier_events(event_type_A, 'F', 'G', 50)
outliers_4 = generate_outlier_events(event_type_A, 'H', 'I', 50)
outliers_5 = generate_outlier_events(event_type_A, 'J', 'K', 25)

# Combine all events
all_events = (
        events_1 + outliers_1 +
        events_2 + outliers_2 +
        events_3 + outliers_3 +
        events_4 + outliers_4 +
        events_5 + outliers_5
)

# Write events to a JSON file
output_file = 'events_with_outliers.json'
with open(output_file, 'w') as f:
    json.dump(all_events, f, indent=4)

print(f"{len(all_events)} events have been written to {output_file}")