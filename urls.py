# project_name/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('streaming.urls')),  # Changed to include the streaming URLs at the root level
]
