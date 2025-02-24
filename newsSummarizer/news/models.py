from django.db import models

class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    rss_feed_url = models.URLField()
    published_at = models.DateTimeField()
    content = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)  # New field added

    def __str__(self):
        return self.title
    
from .models import News  # Assuming News is your article model
from django.utils.timezone import now, timedelta

class TrendingNews(models.Model):
    article = models.OneToOneField(News, on_delete=models.CASCADE)
    clicks = models.IntegerField(default=1)  # Default clicks = 1
    last_reset = models.DateTimeField(auto_now_add=True)

