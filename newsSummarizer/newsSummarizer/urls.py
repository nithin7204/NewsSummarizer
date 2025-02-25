from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Include home app URLs
    path('news/', include('news.urls')),  # Include news app URLs
]
