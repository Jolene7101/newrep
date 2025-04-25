# Scrapfly API Integration for FireproofAI Lead Generation

This module provides a reliable, scalable way to scrape data from various social media platforms and news sources using the Scrapfly API, a professional web scraping service that handles anti-bot measures and rate limits.

## Key Features

- **Multi-Platform Coverage**: Scrape from LinkedIn, Reddit, Twitter/X, and Google News
- **AI-Powered Extraction**: Leverages Scrapfly's AI extraction capabilities for structured data
- **Normalized Output**: All scrapers return data in a consistent format for easy processing
- **Error Handling**: Robust error handling and logging across all scrapers
- **Location & Tag Extraction**: Automatically identifies state mentions and relevant industry keywords

## Setup Instructions

1. Add your Scrapfly API key to the `.env` file in the project root:
   ```
   SCRAPFLY_API_KEY=your-api-key-here
   ```

2. Install required dependencies:
   ```
   pip install python-dotenv scrapfly-sdk requests
   ```

## Usage Examples

### LinkedIn Scraping

```python
from fireproofai.lead_sources.scrapfly.linkedin_scraper import LinkedInScraper

# Initialize the scraper
linkedin_scraper = LinkedInScraper()

# Search for fireproofing-related posts
results = linkedin_scraper.scrape_posts("fireproofing steel construction", limit=10)

# Scrape posts from a specific profile
profile_posts = linkedin_scraper.scrape_profile_posts("https://www.linkedin.com/company/skanska/", limit=5)
```

### Reddit Scraping

```python
from fireproofai.lead_sources.scrapfly.reddit_scraper import RedditScraper

# Initialize the scraper
reddit_scraper = RedditScraper()

# Search for fireproofing-related posts
results = reddit_scraper.scrape_posts("fireproofing steel high rise", limit=10)

# Scrape a specific thread including comments
thread_data = reddit_scraper.scrape_thread("https://www.reddit.com/r/Construction/comments/example")

# Scrape posts from a subreddit
subreddit_posts = reddit_scraper.scrape_subreddit("Construction", limit=15)
```

### Twitter/X Scraping

```python
from fireproofai.lead_sources.scrapfly.twitter_scraper import TwitterScraper

# Initialize the scraper
twitter_scraper = TwitterScraper()

# Search for fireproofing-related tweets
results = twitter_scraper.scrape_tweets("fireproofing commercial building", limit=20)

# Scrape tweets from a user's timeline
timeline_tweets = twitter_scraper.scrape_user_timeline("SteelConstructUS", limit=10)

# Scrape a tweet thread
thread_tweets = twitter_scraper.scrape_tweet_thread("https://twitter.com/username/status/123456789")
```

### Google News Scraping

```python
from fireproofai.lead_sources.scrapfly.google_news_scraper import GoogleNewsScraper

# Initialize the scraper
news_scraper = GoogleNewsScraper()

# Search for fireproofing-related news
results = news_scraper.scrape_news("steel fireproofing construction", limit=15, time_range="7d")

# Scrape a specific article
article_data = news_scraper.scrape_article("https://example.com/news/article")

# Scrape articles from a topic section
topic_articles = news_scraper.scrape_topic("business", limit=10)
```

## Output Format

All scrapers return data in the following normalized format:

```json
{
  "source": "linkedin|reddit|twitter|google_news",
  "url": "https://...",
  "title": "Post or article title",
  "text": "Full text content",
  "author": "Author name or source",
  "timestamp": "2025-04-24T20:30:00Z",
  "tags": ["fireproofing", "steel fireproofing", ...],
  "state": "TX",
  "raw_data": { ... }
}
```

## Integration with Main Application

This module can be integrated with the main FireproofAI application by importing the necessary scrapers and calling their methods from your lead generation pipeline.

## Scrapfly API Documentation

For more details on Scrapfly API capabilities and options, visit:
- [Scrapfly Documentation](https://scrapfly.io/docs)
- [Scrapfly AI Extraction](https://scrapfly.io/docs/scrape-api/ai-extraction)
