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
1. **Primary Data:** * **Reddit API (via PRAW):** Historical and streaming post data from local subreddits (e.g., `r/phr4r`). 
   * *Extracted fields:* Timestamps (UTC), Title (for demographic/intent parsing), and Post Body.
2. **Supplementary Data (Optional Context):**
   * **Open-Meteo API / PAGASA:** Historical weather data to correlate rain/typhoons with post volume.
   * **PH Holiday Calendar:** To flag long weekends or holidays (e.g., Valentine's Day, Christmas).