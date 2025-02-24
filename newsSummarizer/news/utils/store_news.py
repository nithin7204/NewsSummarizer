# utils/store_news.py
from ..models import News
from datetime import datetime

def store_news(articles):
    for article in articles:
        title = article["title"]
        description = article["description"]
        url = article["url"]
        rss_feed_url = article["rss_feed_url"]
        published_at = article["published_at"]
        content = article["content"]
        image_url = article.get("image_url", "")  # Now storing the image URL

        # Convert published_at to datetime
        published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))

        # Save or update the news article in the database
        News.objects.update_or_create(
            title=title,
            defaults={
                "description": description,
                "url": url,
                "rss_feed_url": rss_feed_url,
                "published_at": published_at,
                "content": content,
                "image_url": image_url  # Store image URL
            }
        )
    
