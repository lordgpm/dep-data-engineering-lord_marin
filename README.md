# Project: Temporal Dynamics of Connection-Seeking in PH r4r Subreddits

## The Problem
Urban isolation is difficult to quantify. By analyzing the timestamps and intent (e.g., friendship, dating, late-night hookups) of r4r posts, this project identifies **"Peak Loneliness Hours."** Solving this helps answer:
* Are there specific hours, days, or weather conditions (e.g., rainy weekends) that trigger spikes in people seeking connection?
* This data can inform when community builders, event organizers, or mental health resources (like hotlines) should scale up availability.

## The Question
Which cities in Metro Manila exhibit the highest volume of digital connection-seeking posts per capita, and what types of social intent (friendship vs. romance) dominate each local area?

## The Audience
* Urban Planners and LGU Health Boards: To identify which specific high-density cities are experiencing structural isolation, allowing them to target local mental health initiatives or public social spaces. It could also lead to LGUs taking note of areas where there are more posts looking for hookups as it could help them start or expand safe sex programs.

* Commercial Developers & Community Builders: Co-working spaces, board game cafes, and lifestyle brands can use this to identify untapped local demand for spaces that facilitate casual, platonic human interaction ("friendliest cities").

## Data Sources
1. **Primary Data:** * **Reddit API (via PRAW):** Historical and streaming post data from local subreddits. 
   * **Location/URL:** https://www.reddit.com/dev/api/
   * *Coverage & Scope (Subreddit Targets):*
      * [*phr4r_2*](https://www.reddit.com/r/phr4r_2/) for category of *All*
      * [*phr4friends*](https://www.reddit.com/r/PhR4Friends/) for category of *Platonic*
      * [*phr4dating*](https://www.reddit.com/r/PhR4Dating/) for category of *Romantic*
      * [*dirtyphpr4r*](https://www.reddit.com/r/dirtyphpr4r/) for category of *Sexual*
   * *Extracted fields:* Timestamps (UTC), Title (for demographic/intent parsing), and Post Body.
   * *Timeframe:*  The project will only get properly-formatted r4r posts as data from the last year (July 2025 to July 2026)
   * **Limitations:** City-level data relies on voluntary location tags in post titles. Additionally, the official Reddit API caps listing endpoints to the 1,000 most recent posts.
2. **Backup Data:** 
   * [**PullPush API**](https://pullpush.io/) for public API of archived Reddit posts
   * [**Arctic Shift**](https://arctic-shift.photon-reddit.com/) public API and download tools for archived Reddit posts.
   * **Role:** Used if PRAW API access is rate-limited, revoked, or fails to fetch older historical posts.
3. **Supplementary Data (Optional Context):**
   * [**Openweather API:**](https://openweathermap.org/api) Historical weather data to correlate rain/typhoons with post volume.
   * [**PH Holiday Calendar:**](https://www.officialgazette.gov.ph/nationwide-holidays/) To flag long weekends or holidays (e.g., Valentine's Day, Christmas).

## Week 5 - API Fundamentals & Request Handling
Completed enhancements to the data ingestion pipeline:
- Updated scripts/ingest.py to collect from all 4 subreddits (phr4r_2, phr4friends, phr4dating, dirtyphpr4r)
- Implemented proper error handling and rate limiting
- Added pagination support for retrieving larger datasets
- Ensured raw data is saved consistently to /data/raw/

## Setup Instructions
To set up the data ingestion environment:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Reddit API credentials**:
   - Copy the example environment file: `cp .env.example .env`
   - Fill in your Reddit API credentials in the `.env` file:
     - `REDDIT_CLIENT_ID`: Your Reddit app client ID
     - `REDDIT_CLIENT_SECRET`: Your Reddit app client secret
     - `REDDIT_USER_AGENT`: A unique user agent string for your app

## Running the Ingestion Script
To run the data ingestion script:

```bash
python scripts/ingest.py
```

This will:
- Fetch posts from all 4 subreddits (phr4r_2, phr4friends, phr4dating, dirtyphpr4r)
- Save individual subreddit data to `/data/raw/`
- Create a combined dataset in `/data/raw/`
- Display progress information during execution

