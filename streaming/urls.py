"""
URL configuration for streaming project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# streaming/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index_view'),
    path('chat/', views.chat_view, name='chat_view'),
    path('chat_javascript/', views.chat_javascript_view, name='chat_javascript_view'),
    path('stream/<str:user_message>/', views.stream_javascript_response, name='stream_javascript_response'),
    path('sse/', views.sse_endpoint, name='sse_endpoint'),
    # other URL patterns...
]

# # streaming/urls.py ### JAVASCRIPT VERSION ###
# from django.urls import path
# from .views import chat_view, stream_response

# urlpatterns = [
#     path('chat/', chat_view, name='chat'),
#     path('stream/<str:user_message>/', stream_response, name='stream_response'),
# ]

