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
3. **Reference Data:**
   * [**PSGC (Philippine Standard Geographic Code), 2Q 2026**](https://psa.gov.ph/classification/psgc/) — official PSA publication listing all regions, provinces, cities, and municipalities. Used to canonicalize city names for location extraction (see `data/reference/metro_manila_gazetteer.csv`).
4. **Supplementary Data (Optional Context):**
   * [**Openweather API:**](https://openweathermap.org/api) Historical weather data to correlate rain/typhoons with post volume.
   * [**PH Holiday Calendar:**](https://www.officialgazette.gov.ph/nationwide-holidays/) To flag long weekends or holidays (e.g., Valentine's Day, Christmas).

## Week 5 - API Fundamentals & Request Handling
Completed enhancements to the data ingestion pipeline:
- Updated scripts/ingest.py to collect from all 4 subreddits (phr4r_2, phr4friends, phr4dating, dirtyphpr4r)
- Implemented proper error handling and rate limiting
- Added pagination support for retrieving larger datasets
- Ensured raw data is saved consistently to /data/raw/

## Week 8 - Transformation & SQL Analysis (M3)

### Data source actually used
Because the official Reddit API caps listings at the 1,000 most recent posts, the
historical corpus was pulled from the **Arctic Shift** archive
(https://arctic-shift.photon-reddit.com/), the documented backup source. Raw
exports (JSON/JSONL) for the four target subreddits live in `data/raw/`. The
archive files exceed GitHub's 100 MB limit, so they are shared in the group
Google Drive folder:
https://drive.google.com/drive/folders/1mLDAGoHzAF9RnPt4DZUdN0IoAUcnrc9_?usp=sharing

### Transformation (`scripts/transform.py`)
A deterministic, reproducible pipeline that turns raw exports into a clean,
analysis-ready dataset:
- Drops stickied/removed moderator posts, records missing id/title/date, deleted
  authors, and empty bodies.
- Deduplicates by `post_id` (Arctic Shift and PRAW exports overlap).
- Parses `seeker_age`, `seeker_gender`, `target_gender`, and `intent_tag` (X4Y)
  from titles via regex; missing tags are kept but flagged.
- Extracts the `city` via gazetteer-based geoparsing: aliases from
  `data/reference/metro_manila_gazetteer.csv` (canonical names from the PSGC
  2Q 2026 publication) are matched against `title + selftext` with
  word-boundary regex; blank when no city is mentioned.
- Converts `created_utc` to Asia/Manila (UTC+8) and derives `date_manila`,
  `hour_manila`, `day_of_week`, `year`, `month`.
- Maps each subreddit to an intent `category` (all/platonic/romantic/sexual).

Outputs:
- `data/processed/posts_clean.csv` — the clean dataset (211,528 rows). At
  ~147 MB it exceeds GitHub's 100 MB file limit, so it is shared via Google
  Drive:
  https://drive.google.com/file/d/1D_cHcuNjtt3uV31ygeJM8Wu5PBvXJkf9/view?usp=sharing
- `data/processed/cleaning_log.md` — every cleaning decision, row counts per
  step, and validation checks. Same input always produces the same output.

### Processed schema (`posts_clean.csv`)
Key columns: `post_id`, `title`, `selftext`, `author`, `subreddit`, `category`,
`created_utc`, Manila-local time fields (`created_datetime_manila`,
`date_manila`, `hour_manila`, `day_of_week`, `year`, `month`), engagement
metrics (`score`, `num_comments`), title-parsed fields (`seeker_age`,
`seeker_gender`, `target_gender`, `intent_tag`), and `city` (gazetteer-based
geoparsing of title + selftext). The CSV is not tracked in git because of its
size; it is shared via the Drive link above and can be regenerated by running
`scripts/transform.py`.

### SQL analysis (`scripts/analysis.sql` + `scripts/run_sql.py`)
`scripts/run_sql.py` loads the clean CSV into an in-memory SQLite `posts` table
and runs every query in `scripts/analysis.sql`, printing results as tables. It
uses only the Python standard library (no extra dependencies).

```bash
python3 scripts/transform.py   # build the clean dataset + cleaning log
python3 scripts/run_sql.py     # run the Week 8 analysis queries
```

Queries cover: volume by intent category, peak loneliness hours (Asia/Manila),
volume by day of week, Metro Manila cities ranked by volume with intent mix,
intent mix by hour, seeker gender split by intent, monthly trend, and the age
profile of connection seekers.

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

