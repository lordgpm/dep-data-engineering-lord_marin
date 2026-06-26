# Project: Temporal Dynamics of Connection-Seeking in PH r4r Subreddits

## The Problem
Urban isolation is difficult to quantify. By analyzing the timestamps and intent (e.g., friendship, dating, late-night hookups) of r4r posts, this project identifies **"Peak Loneliness Hours."** Solving this helps answer:
* Are there specific hours, days, or weather conditions (e.g., rainy weekends) that trigger spikes in people seeking connection?
* This data can inform when community builders, event organizers, or mental health resources (like hotlines) should scale up availability.

## Data Sources
1. **Primary Data:** * **Reddit API (via PRAW):** Historical and streaming post data from local subreddits (e.g., `r/phr4r`). 
   * *Extracted fields:* Timestamps (UTC), Title (for demographic/intent parsing), and Post Body.
2. **Supplementary Data (Optional Context):**
   * **Open-Meteo API / PAGASA:** Historical weather data to correlate rain/typhoons with post volume.
   * **PH Holiday Calendar:** To flag long weekends or holidays (e.g., Valentine's Day, Christmas).