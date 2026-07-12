"""
Phase 2 — Data Ingestion
Replace this template with your own ingestion logic.
"""

import os
import praw
import json
from datetime import datetime
from dotenv import load_dotenv

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def ingest():
   
    load_dotenv()
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    
    # Target subreddit
    subreddit = reddit.subreddit('phr4r_2')
    
    
    posts_data = []
    for post in subreddit.new(limit=100):
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'selftext': post.selftext,
            'created_utc': post.created_utc,
            'url': post.url,
            'subreddit': str(post.subreddit),
            'score': post.score,
            'num_comments': post.num_comments
        })
    
    # Generate descriptive filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'phr4r_posts_sample_{timestamp}.json'
    filepath = os.path.join(RAW_DATA_DIR, filename)
    
    # Save raw data as JSON
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved {len(posts_data)} posts to {filepath}")


if __name__ == "__main__":
    ingest()
    print("Ingestion complete. Check data/raw/ for output.")