from .models import News
from .utils.store_news import store_news
from .utils.fetch_news import fetch_news
from .utils.content_fetcher import get_final_url, fetch_webpage_content, summarize_content,format_news_content
from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from .models import News, TrendingNews

def article_detail(request, article_id):
    """Display full news article and track clicks."""
    article = get_object_or_404(News, id=article_id)

    # Increment or create click count
    trending, created = TrendingNews.objects.get_or_create(article=article)
    trending.clicks += 1
    trending.save()

    return render(request, "news/article_detail.html", {"article": article})

def trending_news(request):
    """Get trending articles sorted by clicks."""
    # Reset clicks for articles older than 24 hours
    TrendingNews.objects.all().update(last_reset=now())

    trending_articles = TrendingNews.objects.all().order_by("-clicks")
    return render(request, "news/trending_news.html", {"articles": trending_articles})


def fetch_extended_content(request):
    """Fetch full content first, with an option to summarize."""
    query = request.GET.get("rss_feed_url")  # Get RSS feed URL from request
    summarize = request.GET.get("summarize", "false").lower() == "true"  # Check if summarization is requested

    if not query:
        return render(request, "news/news_summary.html", {"error": "Query is required"})

    try:
        # Step 1: Get the final URL using DuckDuckGo search
        final_url = get_final_url(query)
        if not final_url:
            return render(request, "news/news_summary.html", {"error": "No search results found"})

        # Step 2: Fetch content from the webpage
        full_content = fetch_webpage_content(final_url)
        full_content = format_news_content(full_content)

        if "Error" in full_content or "Failed" in full_content:
            return render(request, "news/news_summary.html", {"error": full_content})

        # Step 3: If summary is requested, generate it
        if summarize:
            summarized_content = summarize_content(full_content)
            print(summarized_content)
            return render(request, "news/news_summarized.html", {"summary": summarized_content})

        # Render full content with a "Summarize" button
        return render(request, "news/news_summary.html", {"full_content": full_content, "rss_feed_url": query})

    except Exception as e:
        return render(request, "news/news_summary.html", {"error": str(e)})

import time
import re
def is_perfect_time():
    """Check if the current time is exactly 1:00, 2:00, 3:00, etc."""
    current_time = time.strftime("%H:%M")  # Get current time in HH:MM format
    return re.match(r"^\d{1,2}:00$", current_time)  # Matches times like 1:00, 2:00, 15:00

def news_list(request):
    """Fetch and display news articles, only updating at perfect times."""
    
    stored_articles = News.objects.all().order_by("-published_at")  # Get stored news
    
    # If the time is perfect (e.g., 1:00, 2:00, 3:00), fetch new data
    if is_perfect_time():
        print("Fetching new news data...")  # Debugging
        articles = fetch_news(request)  # Fetch fresh news from API
        store_news(articles)  # Store news in the database
        stored_articles = News.objects.all().order_by("-published_at")  # Retrieve updated news
    else:
        print("Using stored news data...")  # Debugging

    return render(request, "news/news_list.html", {"articles": stored_articles})

from django.utils.timezone import timedelta

def reset_trending_news():
    """Reset trending clicks every 24 hours."""
    TrendingNews.objects.filter(last_reset__lt=now() - timedelta(days=1)).update(clicks=0, last_reset=now())
