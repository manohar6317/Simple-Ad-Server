import schedule
import time
import sqlite3
import datetime
import pytz

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('ad_stats.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ad_stats (
        ad_content TEXT PRIMARY KEY,
        impressions INTEGER,
        clicks INTEGER
    )
''')
conn.commit()

ad_stats = {}

def load_stats():
    cursor.execute("SELECT * FROM ad_stats")
    rows = cursor.fetchall()
    for row in rows:
        ad_stats[row[0]] = {"impressions": row[1], "clicks": row[2]}

load_stats()

def display_ad(ad_content, target_age, target_location):
    user_age = int(input("Enter your age: "))
    user_location = input("Enter your location: ")

    if check_targeting(user_age, user_location, target_age, target_location):
        print(f"Displaying Ad: {ad_content}")
        ad_stats[ad_content]["impressions"] += 1

        click = input("Do you want to click this ad? (yes/no): ")
        if click.lower() == "yes":
            ad_stats[ad_content]["clicks"] += 1

        update_stats(ad_content)

    else:
        print("Ad not relevant to you.")

def check_targeting(user_age, user_location, target_age, target_location):
    if target_age == "any" or (isinstance(target_age, tuple) and target_age[0] <= user_age <= target_age[1]):
        if target_location == "any" or user_location.lower() == target_location.lower():
            return True
    return False

def update_stats(ad_content):
    stats = ad_stats[ad_content]
    cursor.execute('''
        INSERT OR REPLACE INTO ad_stats (ad_content, impressions, clicks)
        VALUES (?, ?, ?)
    ''', (ad_content, stats["impressions"], stats["clicks"]))
    conn.commit()

def get_most_popular_ad():
    cursor.execute("SELECT ad_content FROM ad_stats ORDER BY impressions DESC LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result else None

def get_highest_ctr_ad():
    cursor.execute("SELECT ad_content FROM ad_stats ORDER BY CAST(clicks AS REAL) / impressions DESC LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result and result[0] else None

def get_total_impressions(ad_content):
    cursor.execute("SELECT impressions FROM ad_stats WHERE ad_content = ?", (ad_content,))
    result = cursor.fetchone()
    return result[0] if result else 0


def get_time_in_india(hour, minute):
    india_timezone = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(india_timezone)
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return scheduled_time.strftime("%H:%M")

# Schedule ads (using specific times in India)
scheduled_time_ad1 = get_time_in_india(9, 0) # 9:00 AM IST
scheduled_time_ad2 = get_time_in_india(20, 47) # 5:00 PM IST

schedule.every().day.at(scheduled_time_ad1).do(display_ad, "Ad Content 1 (18-35, NY)", (18, 35), "New York")
schedule.every().day.at(scheduled_time_ad2).do(display_ad, "Ad Content 2 (Any Age, London)", "any", "London")


while True:
    schedule.run_pending()
    time.sleep(1)

    # Print ad statistics every 10 seconds
    if time.time() % 10 == 0:
        print("\n--- Ad Statistics ---")
        for ad, stats in ad_stats.items():
            print(f"{ad}: Impressions - {stats['impressions']}, Clicks - {stats['clicks']}")

        most_popular = get_most_popular_ad()
        highest_ctr = get_highest_ctr_ad()

        print(f"\nMost Popular Ad: {most_popular}")
        print(f"Ad with Highest CTR: {highest_ctr}")

        ad_name = "Ad Content 1 (18-35, NY)"
        total_impressions = get_total_impressions(ad_name)
        print(f"Total impressions for '{ad_name}': {total_impressions}")