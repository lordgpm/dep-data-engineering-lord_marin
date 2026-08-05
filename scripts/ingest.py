"""
Phase 2 — Data Ingestion
Enhanced version for Week 5 - API Fundamentals & Request Handling
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import praw
from praw.models import ListingGenerator

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def ingest_subreddit(subreddit_name, limit=1000):
    """Ingest posts from a specific subreddit"""
    load_dotenv()
    
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
        
        # Target subreddit
        subreddit = reddit.subreddit(subreddit_name)
        
        posts_data = []
        post_count = 0
        
        # Use ListingGenerator to handle pagination
        for post in subreddit.new(limit=limit):
            posts_data.append({
                'id': post.id,
                'title': post.title,
                'selftext': post.selftext,
                'created_utc': post.created_utc,
                'url': post.url,
                'subreddit': str(post.subreddit),
                'score': post.score,
                'num_comments': post.num_comments,
                'author': str(post.author) if post.author else None
            })
            post_count += 1
            
            # Rate limiting - add delay between requests
            time.sleep(0.1)
            
        print(f"Successfully fetched {post_count} posts from r/{subreddit_name}")
        return posts_data
        
    except Exception as e:
        print(f"Error fetching data from r/{subreddit_name}: {str(e)}")
        return []


def save_raw_data(data, subreddit_name):
    """Save raw data to consistent filename format"""
    # Generate descriptive filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{subreddit_name}_posts_{timestamp}.json'
    filepath = os.path.join(RAW_DATA_DIR, filename)
    
    # Save raw data as JSON
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved {len(data)} posts to {filepath}")
    return filepath


def main():
    """Main ingestion function for all subreddits"""
    # Define subreddits to collect data from
    subreddits = ['phr4r_2', 'phr4friends', 'phr4dating', 'dirtyphpr4r']
    
    all_posts_data = []
    
    print("Starting data ingestion from multiple subreddits...")
    
    # Collect data from each subreddit
    for subreddit_name in subreddits:
        print(f"\nFetching data from r/{subreddit_name}...")
        subreddit_data = ingest_subreddit(subreddit_name, limit=1000)
        
        if subreddit_data:
            all_posts_data.extend(subreddit_data)
            # Save individual subreddit data
            save_raw_data(subreddit_data, subreddit_name)
        else:
            print(f"No data retrieved from r/{subreddit_name}")
    
    # Save combined data
    if all_posts_data:
        combined_filename = f'all_ph_r4r_posts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        combined_filepath = os.path.join(RAW_DATA_DIR, combined_filename)
        with open(combined_filepath, 'w', encoding='utf-8') as f:
            json.dump(all_posts_data, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved combined {len(all_posts_data)} posts to {combined_filepath}")
    
    print("\nIngestion complete. Check data/raw/ for output.")


if __name__ == "__main__":
    main()
