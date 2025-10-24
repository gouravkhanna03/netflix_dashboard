import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import numpy as np

fake = Faker()

# ------------------------------
# 1️⃣ Load main Netflix dataset
# ------------------------------
movies_df = pd.read_csv("netflix_with_posters.csv")

# Use only movies with valid titles
movies_df = movies_df[movies_df['title'].notna()]

# Reset index for easier ID assignment
movies_df = movies_df.reset_index(drop=True)
movies_df['movie_id'] = movies_df.index + 1  # unique movie IDs

# ------------------------------
# 2️⃣ Setup date range
# ------------------------------
start_date_obj = datetime.strptime('2018-01-01', '%Y-%m-%d').date()
end_date_obj = datetime.strptime('2025-12-31', '%Y-%m-%d').date()

# ------------------------------
# 3️⃣ Generate Users Table
# ------------------------------
num_users = 12000  # realistic number for small dataset (~100k rows)
users = []

countries = ['USA', 'India', 'UK', 'Canada', 'Germany', 'France', 'Brazil', 'Australia']
age_groups = ['18-25', '26-35', '36-45', '46-60', '60+']
device_types = ['Mobile', 'Web', 'TV', 'Tablet']

for user_id in range(1, num_users + 1):
    signup_date = fake.date_between(start_date=start_date_obj, end_date=end_date_obj)
    users.append({
        'user_id': user_id,
        'name': fake.name(),
        'email': fake.email(),
        'signup_date': signup_date,
        'country': random.choice(countries),
        'age_group': random.choice(age_groups),
        'device_type': random.choice(device_types)
    })

users_df = pd.DataFrame(users)
users_df.to_csv("users.csv", index=False)
print(f"✅ Users table generated: {len(users_df)} rows")

# ------------------------------
# 4️⃣ Generate Subscriptions Table
# ------------------------------
plan_types = ['Basic', 'Standard', 'Premium']
plan_fees = {'Basic': 199, 'Standard': 499, 'Premium': 649}

subscriptions = []

for idx, row in users_df.iterrows():
    plan = random.choice(plan_types)
    start_date = row['signup_date']
    # Random subscription duration in months (6 to 60 months)
    duration_months = random.randint(6, 60)
    end_date = pd.to_datetime(start_date) + pd.DateOffset(months=duration_months)
    # Randomly mark some subscriptions as cancelled
    status = random.choices(['Active', 'Cancelled'], weights=[0.7, 0.3])[0]
    subscriptions.append({
        'subscription_id': idx + 1,
        'user_id': row['user_id'],
        'plan_type': plan,
        'monthly_fee': plan_fees[plan],
        'start_date': start_date,
        'end_date': end_date if status == 'Cancelled' else '',
        'status': status
    })

subscriptions_df = pd.DataFrame(subscriptions)
subscriptions_df.to_csv("subscriptions.csv", index=False)
print(f"✅ Subscriptions table generated: {len(subscriptions_df)} rows")

# ------------------------------
# 5️⃣ Generate Watch History Table
# ------------------------------
num_history_rows = 70000  # to reach ~100k total rows
watch_history = []

for i in range(num_history_rows):
    user = users_df.sample(1).iloc[0]
    movie = movies_df.sample(1).iloc[0]

    watch_date = fake.date_between(start_date=start_date_obj, end_date=end_date_obj)
    duration = movie['duration']
    # If duration in minutes, keep as int, else approximate
    try:
        if isinstance(duration, str) and 'min' in duration:
            movie_duration = int(duration.replace('min','').strip())
        else:
            movie_duration = random.randint(40, 180)
    except:
        movie_duration = random.randint(40, 180)

    watch_duration = random.randint(int(0.1*movie_duration), movie_duration)

    watch_history.append({
        'history_id': i + 1,
        'user_id': user['user_id'],
        'movie_id': movie['movie_id'],
        'watch_date': watch_date,
        'watch_duration_mins': watch_duration,
        'device_type': user['device_type']
    })

watch_history_df = pd.DataFrame(watch_history)
watch_history_df.to_csv("watch_history.csv", index=False)
print(f"✅ Watch history table generated: {len(watch_history_df)} rows")

# ------------------------------
# 6️⃣ Generate Revenue Summary Table
# ------------------------------
months = pd.date_range(start='2018-01-01', end='2025-12-31', freq='MS')
revenue_summary = []

for month_start in months:
    month_end = month_start + pd.DateOffset(months=1) - pd.DateOffset(days=1)
    active_subs = subscriptions_df[(pd.to_datetime(subscriptions_df['start_date']) <= month_end)]
    active_subs = active_subs[(subscriptions_df['status'] == 'Active') | ((subscriptions_df['status'] == 'Cancelled') & (pd.to_datetime(subscriptions_df['end_date']) >= month_start))]
    total_users = len(active_subs)
    new_signups = len(users_df[(pd.to_datetime(users_df['signup_date']) >= month_start) & (pd.to_datetime(users_df['signup_date']) <= month_end)])
    cancellations = len(subscriptions_df[(subscriptions_df['status'] == 'Cancelled') & (pd.to_datetime(subscriptions_df['end_date']) >= month_start) & (pd.to_datetime(subscriptions_df['end_date']) <= month_end)])
    total_revenue = active_subs['monthly_fee'].sum()

    revenue_summary.append({
        'month': month_start.strftime('%Y-%m'),
        'total_users': total_users,
        'new_signups': new_signups,
        'cancellations': cancellations,
        'total_revenue': total_revenue
    })

revenue_summary_df = pd.DataFrame(revenue_summary)
revenue_summary_df.to_csv("revenue_summary.csv", index=False)
print(f"✅ Revenue summary table generated: {len(revenue_summary_df)} rows")
