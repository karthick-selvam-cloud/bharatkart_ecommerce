from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('create/', views.create_chat_room, name='create_chat_room'),
    path('send/<int:room_id>/', views.send_message, name='send_message'),
    path('close/<int:room_id>/', views.close_chat_room, name='close_chat_room'),
    path('chatbot/', views.chatbot_query, name='chatbot_query'),
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('assign/<int:room_id>/', views.assign_chat, name='assign_chat'),
]