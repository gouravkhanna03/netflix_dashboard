import pandas as pd
import random

# Step 1: Load both CSV files
netflix_df = pd.read_csv("netflix_data.csv")
watch_df = pd.read_csv("watch_history.csv")

# Step 2: Extract all valid show_ids from netflix_data
valid_show_ids = netflix_df['show_id'].tolist()

# Step 3: Replace invalid show_id in watch_history with random valid ones
def fix_show_id(show_id):
    if show_id not in valid_show_ids:
        return random.choice(valid_show_ids)  # randomly assign a valid ID
    return show_id

watch_df['show_id'] = watch_df['show_id'].apply(fix_show_id)

# ✅ Optional: Check if all show_ids are now valid
invalid_count = (~watch_df['show_id'].isin(valid_show_ids)).sum()
print(f"✅ All show_ids fixed! Remaining invalid IDs: {invalid_count}")

# Step 4: Save cleaned dataset
watch_df.to_csv("watch_history_cleaned.csv", index=False)
print("🎉 Cleaned watch_history saved as 'watch_history_cleaned.csv'")