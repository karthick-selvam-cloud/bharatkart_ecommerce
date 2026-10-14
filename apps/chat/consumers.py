import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage, ChatNotification

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send chat history
        chat_history = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': chat_history
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            message = data.get('message', '')
            message_id = await self.save_message(message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'message_id': message_id,
                    'user_id': self.user.id,
                    'username': self.user.get_full_name() or self.user.username,
                    'timestamp': str(timezone.now()),
                }
            )
            
            # Create notification for other users
            await self.create_notification(message_id)
        
        elif message_type == 'typing':
            # Send typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'username': self.user.get_full_name() or self.user.username,
                    'is_typing': data.get('is_typing', False),
                }
            )
        
        elif message_type == 'read':
            # Mark messages as read
            message_ids = data.get('message_ids', [])
            await self.mark_messages_as_read(message_ids)
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))
    
    async def typing_indicator(self, event):
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing'],
        }))
    
    @database_sync_to_async
    def get_chat_history(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            messages = room.messages.select_related('sender').order_by('created_at')[:50]
            
            history = []
            for msg in messages:
                history.append({
                    'id': msg.id,
                    'content': msg.content,
                    'sender_id': msg.sender.id,
                    'sender_name': msg.sender.get_full_name() or msg.sender.username,
                    'timestamp': msg.created_at.isoformat(),
                    'is_read': msg.is_read,
                })
            
            return history
        except ChatRoom.DoesNotExist:
            return []
    
    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        message = ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=content,
            message_type='text',
        )
        return message.id
    
    @database_sync_to_async
    def create_notification(self, message_id):
        room = ChatRoom.objects.get(id=self.room_id)
        message = ChatMessage.objects.get(id=message_id)
        
        # Create notification for all room participants except sender
        participants = []
        if room.user != message.sender:
            participants.append(room.user)
        if room.agent and room.agent != message.sender:
            participants.append(room.agent)
        
        for participant in participants:
            ChatNotification.objects.create(
                user=participant,
                room=room,
                message=message,
            )
    
    @database_sync_to_async
    def mark_messages_as_read(self, message_ids):
        ChatMessage.objects.filter(
            id__in=message_ids,
            room_id=self.room_id,
        ).exclude(
            sender=self.user
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )