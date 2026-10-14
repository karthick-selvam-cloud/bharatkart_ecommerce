"""
RAG views for BharatKart AI Concierge
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import KnowledgeBase, ChatSession, ChatMessage
from .intent_engine import IntentEngine
import json
import uuid


def chat_view(request):
    """Render the chat page"""
    session_id = request.session.get('rag_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['rag_session_id'] = session_id
    
    session, created = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            'user': request.user if request.user.is_authenticated else None,
        }
    )
    
    # Get last 20 messages for this session
    messages_qs = session.messages.all()[:50]
    
    # Welcome message if new session
    if created and not messages_qs.exists():
        engine = IntentEngine(
            user=request.user if request.user.is_authenticated else None,
            session=session,
        )
        welcome = engine.process('hello')
        
        ChatMessage.objects.create(
            session=session,
            is_user=False,
            message_type=welcome.get('type', 'text'),
            content=welcome['message'],
            metadata={
                'replies': welcome.get('replies', []),
                'intent': 'greeting',
            },
        )
        messages_qs = session.messages.all()
    
    context = {
        'session': session,
        'chat_messages': messages_qs,
    }
    return render(request, 'rag/chat.html', context)


@csrf_exempt
@require_POST
def query_view(request):
    """Process user query and return AI response"""
    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    if not query:
        return JsonResponse({'error': 'Empty query'}, status=400)
    
    # Get or create session
    session_id = request.session.get('rag_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session['rag_session_id'] = session_id
    
    session, _ = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            'user': request.user if request.user.is_authenticated else None,
        }
    )
    
    # Save user message
    user_msg = ChatMessage.objects.create(
        session=session,
        is_user=True,
        content=query,
    )
    
    # Process with intent engine
    engine = IntentEngine(
        user=request.user if request.user.is_authenticated else None,
        session=session,
    )
    response = engine.process(query)
    
    # Save bot response
    bot_msg = ChatMessage.objects.create(
        session=session,
        is_user=False,
        message_type=response.get('type', 'text'),
        content=response['message'],
        metadata={
            'replies': response.get('replies', []),
            'products': response.get('products', []),
            'orders': response.get('orders', []),
            'order': response.get('order', {}),
            'wallet': response.get('wallet', {}),
            'action_note': response.get('action_note', ''),
        },
        intent=response.get('intent', ''),
    )
    
    # Update session title from first message
    if not session.title:
        session.title = query[:100]
        session.save(update_fields=['title'])
    
    return JsonResponse({
        'success': True,
        'response': response['message'],
        'type': response.get('type', 'text'),
        'replies': response.get('replies', []),
        'products': response.get('products', []),
        'orders': response.get('orders', []),
        'order': response.get('order', {}),
        'wallet': response.get('wallet', {}),
        'action_note': response.get('action_note', ''),
        'intent': response.get('intent', ''),
    })


@require_POST
def clear_chat_view(request):
    """Clear current chat session"""
    session_id = request.session.get('rag_session_id')
    if session_id:
        ChatSession.objects.filter(session_id=session_id).delete()
        del request.session['rag_session_id']
    return JsonResponse({'success': True})