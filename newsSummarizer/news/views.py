from .models import News
from .utils.store_news import store_news
from .utils.fetch_news import fetch_news
from .utils.content_fetcher import get_final_url, fetch_webpage_content, summarize_content,format_news_content
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from .models import News, TrendingNews
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import News, Like, Comment
import time
import re

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

from django.shortcuts import get_object_or_404
from .models import News  # Import your Article model

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

        # Step 3: Retrieve the article from the database (if it exists)
        article = News.objects.filter(url=query).first()  # Fetch article using URL

        # Step 4: If summary is requested, generate it
        if summarize:
            summarized_content = summarize_content(full_content)
            print(summarized_content)
            return render(request, "news/news_summarized.html", {"summary": summarized_content, "article": article})

        # Render full content with the article object
        return render(request, "news/news_summary.html", {
            "full_content": full_content,
            "rss_feed_url": query,
            "article": article,  # Pass article to template
        })

    except Exception as e:
        return render(request, "news/news_summary.html", {"error": str(e)})



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

@login_required
def like_article(request, article_id):
    """
    Handles like functionality. If the user has already liked, it removes the like.
    """
    article = get_object_or_404(News, id=article_id)
    like, created = Like.objects.get_or_create(user=request.user, article=article)

    if not created:
        like.delete()
        return JsonResponse({"message": "Like removed", "likes_count": Like.objects.filter(article=article).count()}, status=200)

    return JsonResponse({"message": "Liked successfully", "likes_count": Like.objects.filter(article=article).count()}, status=201)

@login_required
def add_comment(request, article_id):
    """
    Allows authenticated users to comment on an article.
    """
    if request.method == "POST":
        article = get_object_or_404(News, id=article_id)
        data = json.loads(request.body)
        text = data.get("text", "").strip()

        if text:
            comment = Comment.objects.create(user=request.user, article=article, text=text)
            return JsonResponse({
                "message": "Comment added successfully",
                "comment_id": comment.id,
                "text": comment.text,
                "user": comment.user.username,
                "timestamp": comment.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }, status=201)
        else:
            return JsonResponse({"error": "Comment text cannot be empty"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_comments(request, article_id):
    """
    Retrieves all comments for a given article.
    """
    article = get_object_or_404(News, id=article_id)
    comments = Comment.objects.filter(article=article).order_by("-timestamp")

    comments_data = [
        {
            "user": comment.user.username,
            "text": comment.text,
            "timestamp": comment.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for comment in comments
    ]

    return JsonResponse({"comments": comments_data}, status=200)
