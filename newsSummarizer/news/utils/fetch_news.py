import requests
from django.shortcuts import render
from ..models import News, TrendingNews

def fetch_news(request):  
    API_KEY = "defa7fc8e087498badbd1f5eb907f302"  # Replace with your actual API key
    country = request.GET.get("country", "india") 
    
    print(country) # Default to global

    if country == "india":
        url = f"https://newsapi.org/v2/top-headlines?sources=bbc-news,the-times-of-india,google-news-in&apiKey={API_KEY}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={API_KEY}"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])  # Get the list of articles

        valid_articles = []
        
        for article_data in articles:
            source = article_data.get("source", {})  # Get the nested "source" field
            title = article_data.get("title")
            description = article_data.get("description")
            url = article_data.get("url")
            image_url = article_data.get("urlToImage")  # This could be useful later
            published_at = article_data.get("publishedAt")
            content = article_data.get("content")

            # Check if all required fields are present
            if title and description and url and published_at and content:
                article, created = News.objects.get_or_create(
                    title=title,
                    defaults={
                        "description": description,
                        "url": url,
                        "published_at": published_at,
                        "image_url": image_url,
                        "content": content
                    }
                )

                # If the article is newly created, add it to TrendingNews with clicks = 1
                if created:
                    TrendingNews.objects.create(article=article, clicks=1)

                valid_articles.append({
                    "title": title,
                    "description": description,
                    "url": url,
                    "rss_feed_url": source.get("name", "Unknown Source"),
                    "published_at": published_at,
                    "content": content,
                    "image_url": image_url  # Optional, can be stored/displayed
                })
        
        return render(request, "news_list.html", {"articles": valid_articles})  # Render valid articles
    
    return render(request, "news_list.html", {"articles": []})
