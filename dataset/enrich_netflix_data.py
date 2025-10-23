import pandas as pd
import requests
import time

# -------------------------------
# CONFIG
# -------------------------------
INPUT_FILE = "netflix_data.csv"       # Your original CSV
OUTPUT_FILE = "netflix_enriched_sample.csv"  # New enriched sample file
API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI4MGIwZGE4OWE0YTJhMGYyMTIyMWI2M2M1ZjA5ODkyZSIsIm5iZiI6MTc1OTI0NTU1MC45MjYsInN1YiI6IjY4ZGJmNGVlY2I5YTY0ZDM0NzUzMTIzNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.CxJAWGsUkWCmlsaRjZ2_Z4eSPeTUMYlZ-XVgtFWhC0M"

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv(INPUT_FILE)

# Filter only rows where poster_url is NOT blank
df_filtered = df[df['poster_url'].notna() & (df['poster_url'] != "")].head(200)
print(f"Processing {len(df_filtered)} rows with poster URLs...")

# Add new columns
df_filtered['updated_type'] = ""
df_filtered['duration_mins'] = ""
df_filtered['content_rating'] = ""

# -------------------------------
# TMDB Fetch Function
# -------------------------------
def fetch_tmdb_metadata(title, year):
    url = "https://api.themoviedb.org/3/search/multi"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {"query": title, "year": year}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()

        if not data.get("results"):
            return None

        item = data["results"][0]
        tmdb_id = item["id"]
        media_type = item.get("media_type", "Unknown")

        # Fetch details for runtime and rating
        details_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
        details_resp = requests.get(details_url, headers=headers, timeout=10)
        if details_resp.status_code != 200:
            return media_type, None, None
        details = details_resp.json()

        runtime = None
        content_rating = None

        if media_type == "movie":
            runtime = details.get("runtime")
        elif media_type == "tv":
            ep_times = details.get("episode_run_time")
            runtime = ep_times[0] if ep_times else None

        # Get certification (content rating)
        release_info_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/release_dates" if media_type == "movie" else f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/content_ratings"
        release_info = requests.get(release_info_url, headers=headers, timeout=10)
        if release_info.status_code == 200:
            rel_json = release_info.json()
            results = rel_json.get("results", [])
            if results:
                if media_type == "movie":
                    us_release = next((x for x in results if x["iso_3166_1"] == "US"), None)
                    if us_release and us_release.get("release_dates"):
                        content_rating = us_release["release_dates"][0].get("certification")
                else:  # TV shows
                    us_rating = next((x for x in results if x["iso_3166_1"] == "US"), None)
                    if us_rating:
                        content_rating = us_rating.get("rating")

        return media_type, runtime, content_rating

    except Exception as e:
        print("Error:", e)
        return None

# -------------------------------
# Process Rows
# -------------------------------
for idx, row in df_filtered.iterrows():
    title = row['title']
    year = row['release_year']

    meta = fetch_tmdb_metadata(title, year)
    if meta:
        df_filtered.at[idx, 'updated_type'] = meta[0]
        df_filtered.at[idx, 'duration_mins'] = meta[1]
        df_filtered.at[idx, 'content_rating'] = meta[2]

    print(f"✅ Processed: {title}")
    time.sleep(0.5)  # to respect API limits

# -------------------------------
# Save Result
# -------------------------------
df_filtered.to_csv(OUTPUT_FILE, index=False)
print(f"🎉 Done! Enriched sample saved as: {OUTPUT_FILE}")
