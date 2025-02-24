from django.urls import path
from . import views
from .views import fetch_extended_content, news_list, summarize_content,article_detail, trending_news

urlpatterns = [
    path('', news_list, name='news_list'),
    path('fetch_extended_content/', fetch_extended_content, name='fetch_extended_content'),
    path('summarize/', summarize_content, name='summarize_news'),  # ✅ Add this
    path("news/<int:article_id>/", article_detail, name="article_detail"),
    path("trending-news/", trending_news, name="trending_news"),
]

