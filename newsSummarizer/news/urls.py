from django.urls import path
from . import views
from .views import fetch_extended_content, news_list, summarize_content,article_detail, trending_news
from .views import like_article, add_comment, get_comments

urlpatterns = [
    path('', news_list, name='news_list'),

    path('fetch_extended_content/', fetch_extended_content, name='fetch_extended_content'),
    path('summarize/', summarize_content, name='summarize_news'),  # ✅ Add this

    path("news/<int:article_id>/", article_detail, name="article_detail"),
    path("trending-news/", trending_news, name="trending_news"),

    path('news/<int:article_id>/like/', like_article, name='news_like'),
    path('news/<int:article_id>/comment/', add_comment, name='news_comment'),
    path('news/<int:article_id>/comments/', get_comments, name='get_comments'),
]

