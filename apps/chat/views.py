from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import ChatRoom, ChatMessage, ChatNotification, QuickReply, ChatBotResponse
from apps.notifications.sms_service import SMSNotifications
import json

@login_required
def chat_home(request):
    """Display user's chat rooms"""
    chat_rooms = ChatRoom.objects.filter(user=request.user).order_by('-last_activity')
    
    # Get unread counts
    for room in chat_rooms:
        room.unread_count = room.get_unread_count(request.user)
    
    context = {
        'chat_rooms': chat_rooms,
        'active_room': None,
    }
    return render(request, 'chat/chat_home.html', context)

@login_required
def chat_room(request, room_id):
    """Display specific chat room"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user has access
    if room.user != request.user and room.agent != request.user:
        return redirect('chat_home')
    
    # Mark notifications as read
    ChatNotification.objects.filter(
        user=request.user,
        room=room,
        is_read=False
    ).update(is_read=True)
    
    # Get all user's chat rooms for sidebar
    chat_rooms = ChatRoom.objects.filter(
        Q(user=request.user) | Q(agent=request.user)
    ).order_by('-last_activity')
    
    for chat_room in chat_rooms:
        chat_room.unread_count = chat_room.get_unread_count(request.user)
    
    # Get quick replies for agents
    quick_replies = []
    if request.user.is_staff or request.user.role == 'admin':
        quick_replies = QuickReply.objects.filter(is_active=True)
    
    context = {
        'room': room,
        'chat_rooms': chat_rooms,
        'quick_replies': quick_replies,
        'active_room': room,
    }
    return render(request, 'chat/chat_room.html', context)

@login_required
@require_POST
def create_chat_room(request):
    """Create new chat room"""
    try:
        data = json.loads(request.body)
        subject = data.get('subject', 'General Inquiry')
        room_type = data.get('room_type', 'general')
        priority = data.get('priority', 'medium')
        message = data.get('message', '')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    room = ChatRoom.objects.create(
        user=request.user,
        subject=subject,
        room_type=room_type,
        priority=priority,
    )
    
    # Create first message
    if message:
        ChatMessage.objects.create(
            room=room,
            sender=request.user,
            content=message,
        )
    
    return JsonResponse({
        'success': True,
        'room_id': room.id,
    })

@login_required
@require_POST
def send_message(request, room_id):
    """Send message in chat room"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user has access
    if room.user != request.user and room.agent != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        message_type = data.get('message_type', 'text')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    # Check if room is closed
    if room.status == 'closed':
        return JsonResponse({'error': 'Chat room is closed'}, status=400)
    
    message = ChatMessage.objects.create(
        room=room,
        sender=request.user,
        content=content,
        message_type=message_type,
    )
    
    # Update room status
    if room.status == 'open':
        room.status = 'active'
        room.save()
    
    # Create notification for other participant
    other_user = room.agent if request.user == room.user else room.user
    if other_user:
        ChatNotification.objects.create(
            user=other_user,
            room=room,
            message=message,
        )
        
        # Send SMS notification if offline (implement this based on your logic)
        # sms_service = SMSNotifications()
        # sms_service.send_chat_notification(other_user, room)
    
    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'timestamp': message.created_at.isoformat(),
    })

@login_required
@require_POST
def close_chat_room(request, room_id):
    """Close chat room"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if room.user != request.user and room.agent != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        data = json.loads(request.body)
        rating = data.get('rating')
        feedback = data.get('feedback', '')
    except json.JSONDecodeError:
        rating = None
        feedback = ''
    
    room.close_room(rating=rating, feedback=feedback)
    
    return JsonResponse({
        'success': True,
        'message': 'Chat room closed',
    })

@login_required
@require_POST
def chatbot_query(request):
    """Handle chatbot queries"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').lower()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    # Search for matching keyword
    bot_response = ChatBotResponse.objects.filter(
        is_active=True,
        keyword__icontains=query
    ).order_by('-priority').first()
    
    if bot_response:
        return JsonResponse({
            'success': True,
            'response': bot_response.response,
            'is_bot': True,
        })
    
    # Default response
    return JsonResponse({
        'success': True,
        'response': "I'm not sure about that. Let me connect you with a human agent.",
        'is_bot': True,
        'suggest_agent': True,
    })

# Admin views
@login_required
def agent_dashboard(request):
    """Agent dashboard for managing chats"""
    if not (request.user.is_staff or request.user.role == 'admin'):
        return redirect('chat_home')
    
    open_chats = ChatRoom.objects.filter(
        status__in=['open', 'active'],
        agent__isnull=True
    ).order_by('priority', '-last_activity')
    
    my_chats = ChatRoom.objects.filter(
        agent=request.user,
        status='active'
    ).order_by('-last_activity')
    
    context = {
        'open_chats': open_chats,
        'my_chats': my_chats,
    }
    return render(request, 'chat/agent_dashboard.html', context)

@login_required
@require_POST
def assign_chat(request, room_id):
    """Assign chat to agent"""
    if not (request.user.is_staff or request.user.role == 'admin'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    room = get_object_or_404(ChatRoom, id=room_id)
    room.agent = request.user
    room.status = 'active'
    room.save()
    
    return JsonResponse({'success': True})