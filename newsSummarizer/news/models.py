from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

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

class TrendingNews(models.Model):
    article = models.OneToOneField(News, on_delete=models.CASCADE)
    clicks = models.IntegerField(default=1)  # Default clicks = 1
    last_reset = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(News, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')  # Prevents duplicate likes from the same user

    def __str__(self):
        return f"{self.user.username} liked {self.article.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(News, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.article.title}"
