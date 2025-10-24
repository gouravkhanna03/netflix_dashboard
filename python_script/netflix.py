import pandas as pd
import requests
import time
import os

# === CONFIG ===
API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4MGIwZGE4OWE0YTJhMGYyMTIyMWI2M2M1ZjA5ODkyZSIsIm5iZiI6MTc1OTI0NTU1MC45MjYsInN1YiI6IjY4ZGJmNGVlY2I5YTY0ZDM0NzUzMTIzNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.CxJAWGsUkWCmlsaRjZ2_Z4eSPeTUMYlZ-XVgtFWhC0M"
INPUT_FILE = "netflix_movies_detailed_up_to_2025.csv"
OUTPUT_FILE = "netflix_with_posters.csv"
SAVE_EVERY = 50  # auto-save every 50 rows

# === Step 1: Load data ===
if os.path.exists(OUTPUT_FILE):
    print("🔄 Resuming from previous progress...")
    df = pd.read_csv(OUTPUT_FILE)
else:
    df = pd.read_csv(INPUT_FILE)
    if "poster_url" not in df.columns:
        df["poster_url"] = ""

total_rows = len(df)
print(f"📊 Total rows to process: {total_rows}")

# === Function: Get poster from TMDB ===
def get_poster(title):
    url = f"https://api.themoviedb.org/3/search/multi?query={title}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json;charset=utf-8"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        results = data.get("results")
        if results and len(results) > 0:
            poster_path = results[0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception as e:
        print(f"⚠️ Error for {title}: {e}")
    return ""

# === Step 2: Process rows ===
for i, row in df.iterrows():
    # Skip if poster already exists
    if pd.notna(row["poster_url"]) and row["poster_url"] != "":
        continue

    title = str(row["title"])
    poster_url = get_poster(title)
    df.at[i, "poster_url"] = poster_url

    print(f"[{i+1}/{total_rows}] ✅ {title} → {poster_url if poster_url else '❌ Not found'}")

    # Auto-save every SAVE_EVERY rows
    if (i + 1) % SAVE_EVERY == 0:
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"💾 Auto-saved progress at row {i+1}/{total_rows}")

    # Small delay to avoid hitting TMDB rate limit
    time.sleep(0.3)

# === Step 3: Final Save ===
df.to_csv(OUTPUT_FILE, index=False)
print("\n🎉 All done! Posters saved to:", OUTPUT_FILE)
