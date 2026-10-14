from django.urls import path
from . import views

app_name = 'rag'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('query/', views.query_view, name='query'),
    path('clear/', views.clear_chat_view, name='clear_chat'),
]