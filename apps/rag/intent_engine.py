"""
AI Intent Engine for BharatKart Concierge
Detects user intent and generates rich responses
"""

import re
from decimal import Decimal
from django.db.models import Q, Sum
from .models import KnowledgeBase


class IntentEngine:
    """Advanced intent detection and response generation"""

    INTENTS = {
        'track_order': {
            'patterns': [
                r'\b(track|tracking|where.*order|order.*status|status.*order|my order)\b',
                r'\border\s*(number|id|#)\s*[:\-]?\s*([A-Z0-9]+)\b',
            ],
            'keywords': ['track', 'tracking', 'order status', 'where is my order'],
        },
        'return_policy': {
            'patterns': [r'\b(return|refund|exchange|money back|send back)\b'],
            'keywords': ['return', 'refund', 'exchange'],
        },
        'delivery_time': {
            'patterns': [
                r'\b(delivery|shipping|how long|when.*arrive|when.*receive|dispatch)\b',
                r'\b(how many days|expected delivery|delivery time)\b',
            ],
            'keywords': ['delivery', 'shipping', 'how long'],
        },
        'payment_methods': {
            'patterns': [
                r'\b(payment|pay|upi|card|netbanking|cod|cash on delivery|emi)\b',
                r'\b(how.*pay|payment.*option|payment.*method)\b',
            ],
            'keywords': ['payment', 'upi', 'card', 'cod'],
        },
        'wallet_balance': {
            'patterns': [
                r'\b(wallet|balance|my money|my funds|add money)\b',
                r'\b(how much.*have|check.*balance)\b',
            ],
            'keywords': ['wallet', 'balance', 'add money'],
        },
        'product_search': {
            'patterns': [
                r'\b(show|find|search|looking for|need|want|recommend|suggest)\b.*\b(phone|laptop|shirt|dress|shoes|watch|headphone|camera|beauty|book)\b',
                r'\b(best|top|cheap|premium|luxury)\b.*\b(phone|laptop|product|item)\b',
            ],
            'keywords': ['show me', 'recommend', 'looking for', 'best'],
        },
        'order_cancel': {
            'patterns': [r'\b(cancel|stop|abort)\b.*\b(order|purchase)\b'],
            'keywords': ['cancel order', 'cancel my order'],
        },
        'coupon_promo': {
            'patterns': [r'\b(coupon|promo|discount|offer|sale|deal)\b'],
            'keywords': ['coupon', 'discount', 'offer'],
        },
        'greeting': {
            'patterns': [r'^\s*(hi|hello|hey|namaste|good morning|good evening)\b'],
            'keywords': ['hi', 'hello', 'hey'],
        },
        'thanks': {
            'patterns': [r'\b(thanks|thank you|thx|appreciate)\b'],
            'keywords': ['thanks', 'thank you'],
        },
    }

    def __init__(self, user=None, session=None):
        self.user = user
        self.session = session
        self.session_context = session.context if session else {}

    def detect_intent(self, message):
        """Detect the intent of a user message"""
        message_lower = message.lower().strip()
        for intent_name, intent_data in self.INTENTS.items():
            for pattern in intent_data['patterns']:
                if re.search(pattern, message_lower):
                    return intent_name
        return 'knowledge_base'

    def extract_order_number(self, message):
        """Extract order number from message"""
        match = re.search(r'\b(ORD[A-Z0-9]{6,20})\b', message.upper())
        if match:
            return match.group(1)
        match = re.search(r'\border\s*[#:]?\s*([A-Z0-9]{4,20})\b', message.upper())
        if match:
            return match.group(1)
        return None

    def extract_product_query(self, message):
        """Extract product search terms"""
        stop_words = ['show', 'me', 'find', 'search', 'looking', 'for', 'need',
                      'want', 'recommend', 'suggest', 'best', 'top', 'some', 'a',
                      'an', 'the', 'i', 'am', 'is', 'are', 'please', 'can', 'you']
        words = message.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return ' '.join(keywords) if keywords else message

    # ============================================================
    # RESPONSE HANDLERS
    # ============================================================

    def handle_track_order(self, message):
        """Handle order tracking"""
        order_number = self.extract_order_number(message)

        if not self.user or not self.user.is_authenticated:
            return {
                'message': "I'd love to help you track your order! 🔍\n\nPlease **log in** to your BharatKart account so I can look up your orders.",
                'type': 'text',
            }

        if not order_number:
            from apps.orders.models import Order
            recent_orders = Order.objects.filter(user=self.user).order_by('-created_at')[:5]
            if not recent_orders:
                return {
                    'message': "You haven't placed any orders yet. 📦\n\nWould you like me to help you **find something special**?",
                    'type': 'text',
                }
            orders_data = [{
                'id': o.id,
                'order_number': o.order_number,
                'status': o.get_status_display(),
                'status_key': o.status,
                'total': str(o.total),
                'date': o.created_at.strftime('%b %d, %Y'),
            } for o in recent_orders]
            return {
                'message': f"I found **{len(recent_orders)}** recent order(s):",
                'type': 'order_list',
                'orders': orders_data,
            }

        from apps.orders.models import Order
        try:
            order = Order.objects.get(order_number__iexact=order_number, user=self.user)
            return {
                'message': f"Here's your order update for **#{order.order_number}**:",
                'type': 'order_detail',
                'order': {
                    'id': order.id,
                    'order_number': order.order_number,
                    'status': order.get_status_display(),
                    'status_key': order.status,
                    'total': str(order.total),
                    'date': order.created_at.strftime('%B %d, %Y'),
                },
            }
        except Order.DoesNotExist:
            return {
                'message': f"I couldn't find order **{order_number}** in your account. 🤔",
                'type': 'text',
            }

    def handle_return_policy(self, message):
        return {
            'message': "Our **7-Day Return Policy** ensures complete peace of mind. 💎\n\n**Return Window**\n• 7 days from delivery\n• Items must be unused\n\n**Refund Timeline**\n• UPI/Card: 5-7 business days\n• Wallet: Instant",
            'type': 'quick_replies',
            'replies': [
                {'label': 'Start a Return', 'value': 'I want to return an item'},
                {'label': 'View My Orders', 'value': 'Show my orders'},
            ],
        }

    def handle_delivery_time(self, message):
        return {
            'message': "Here's our delivery promise: 🚚\n\n**Standard** — 3-5 business days\n**Express** — 1-2 business days\n**Same-Day** — Mumbai, Delhi, Bangalore\n\nAll shipments include **real-time tracking**.",
            'type': 'quick_replies',
            'replies': [
                {'label': 'Track My Order', 'value': 'Track my order'},
                {'label': 'Express Shipping', 'value': 'Tell me about express delivery'},
            ],
        }

    def handle_payment_methods(self, message):
        return {
            'message': "We accept **all major payment methods**: 💳\n\n• **UPI** — GPay, PhonePe, Paytm\n• **Cards** — Visa, Mastercard, RuPay\n• **Net Banking** — All major banks\n• **COD** — ₹49 fee\n• **EMI** — No-cost available\n• **Wallet** — Instant checkout",
            'type': 'quick_replies',
            'replies': [
                {'label': 'Add Wallet Money', 'value': 'How to add money to wallet?'},
                {'label': 'EMI Options', 'value': 'Tell me about EMI'},
            ],
        }

    def handle_wallet_balance(self, message):
        if not self.user or not self.user.is_authenticated:
            return {
                'message': "Your **BharatKart Wallet** offers instant checkout and cashback! 💰\n\nPlease **log in** to check your balance.",
                'type': 'text',
            }
        from apps.accounts.models import Wallet
        wallet, _ = Wallet.objects.get_or_create(user=self.user)
        return {
            'message': "Here's your wallet summary: 💰",
            'type': 'wallet_info',
            'wallet': {
                'balance': str(wallet.balance),
                'total_added': str(wallet.total_added),
                'total_spent': str(wallet.total_spent),
            },
            'replies': [
                {'label': 'Add Money', 'value': 'I want to add money to wallet'},
                {'label': 'Transaction History', 'value': 'Show my transactions'},
            ],
        }

    def handle_product_search(self, message):
        from apps.products.models import Product
        query = self.extract_product_query(message)

        products = Product.objects.filter(is_active=True).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        ).order_by('-is_featured', '-sales_count')[:6]

        if not products:
            products = Product.objects.filter(is_active=True, is_bestseller=True)[:6]

        if not products:
            products = Product.objects.filter(is_active=True, is_featured=True)[:6]

        if not products:
            return {
                'message': "I couldn't find specific products matching your request. 🛍️\n\nWould you like to explore our **featured collection**?",
                'type': 'quick_replies',
                'replies': [
                    {'label': 'View Collections', 'value': 'Show all categories'},
                    {'label': 'Best Sellers', 'value': 'Show best sellers'},
                ],
            }

        products_data = [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'price': str(p.price),
            'mrp': str(p.mrp),
            'discount': int(p.discount) if p.discount else 0,
            'image': p.get_main_image() or '',
            'rating': float(p.average_rating) if p.average_rating else 0,
            'category': p.category.name if p.category else '',
            'brand': p.brand.name if p.brand else '',
        } for p in products]

        return {
            'message': f"I've found **{len(products)}** exquisite pieces for you: ✨",
            'type': 'product_grid',
            'products': products_data,
        }

    def handle_order_cancel(self, message):
        if not self.user or not self.user.is_authenticated:
            return {
                'message': "Please **log in** to cancel orders.",
                'type': 'text',
            }
        from apps.orders.models import Order
        cancellable = Order.objects.filter(
            user=self.user, status__in=['pending', 'confirmed']
        ).order_by('-created_at')

        if not cancellable:
            return {
                'message': "You don't have any orders that can be cancelled right now. 🤷\n\nOrders can only be cancelled within 1 hour of placement.",
                'type': 'text',
            }

        orders_data = [{
            'id': o.id,
            'order_number': o.order_number,
            'status': o.get_status_display(),
            'status_key': o.status,
            'total': str(o.total),
            'date': o.created_at.strftime('%b %d, %Y'),
        } for o in cancellable]

        return {
            'message': "Here are orders you can still cancel: 🚫",
            'type': 'order_list',
            'orders': orders_data,
        }

    def handle_coupon_promo(self, message):
        return {
            'message': "Here are today's exclusive offers: 🎁\n\n**WELCOME10** — 10% off first order\n**FESTIVE20** — 20% off above ₹2000\n**WALLET5** — 5% extra cashback",
            'type': 'quick_replies',
            'replies': [
                {'label': 'Browse Sale', 'value': 'Show sale items'},
                {'label': 'Featured Products', 'value': 'Show featured products'},
            ],
        }

    def handle_greeting(self, message):
        name = ''
        if self.user and self.user.is_authenticated:
            name = f", {self.user.first_name or self.user.username}"
        return {
            'message': f"Namaste{name}! 🙏 Welcome to **BharatKart's AI Concierge**.\n\nHow may I serve you today?",
            'type': 'quick_replies',
            'replies': [
                {'label': 'Track My Order', 'value': 'Track my order'},
                {'label': 'Check Wallet', 'value': 'Show my wallet balance'},
                {'label': 'Best Sellers', 'value': 'Show best sellers'},
                {'label': 'Return Policy', 'value': 'What is your return policy?'},
            ],
        }

    def handle_thanks(self, message):
        return {
            'message': "It was my pleasure to assist you! 💫\n\nIs there anything else I can help you with?",
            'type': 'quick_replies',
            'replies': [
                {'label': 'Browse Products', 'value': 'Show featured products'},
                {'label': 'No, Thank You', 'value': 'Goodbye'},
            ],
        }

    def handle_knowledge_base(self, message):
        """Search knowledge base and use AI if available"""
        # Try AI first
        try:
            from .llm_client import get_llm_client
            llm = get_llm_client()
            if llm.is_available():
                # Get relevant KB context
                words = [w for w in message.lower().split() if len(w) > 3]
                query = Q(is_active=True)
                if words:
                    search_q = Q()
                    for word in words:
                        search_q |= Q(title__icontains=word) | Q(content__icontains=word) | Q(keywords__icontains=word)
                    query &= search_q
                articles = KnowledgeBase.objects.filter(query)[:3]
                context = "\n\n".join([f"{a.title}: {a.content}" for a in articles])

                ai_response = llm.generate(
                    system_prompt=(
                        "You are BharatKart's luxury AI concierge. Answer customer questions "
                        "warmly and concisely. Use markdown for formatting."
                    ),
                    user_message=message,
                    context=context,
                    max_tokens=400,
                )
                if ai_response:
                    return {
                        'message': ai_response,
                        'type': 'quick_replies',
                        'replies': [
                            {'label': 'Track Order', 'value': 'Track my order'},
                            {'label': 'Browse Products', 'value': 'Show featured products'},
                            {'label': 'Check Wallet', 'value': 'Show my wallet balance'},
                        ],
                    }
        except Exception:
            pass  # Fall through to KB search

        # Fallback: KB search
        words = [w for w in message.lower().split() if len(w) > 3]
        query = Q(is_active=True)
        if words:
            search_q = Q()
            for word in words:
                search_q |= Q(title__icontains=word) | Q(content__icontains=word) | Q(keywords__icontains=word)
            query &= search_q
        articles = KnowledgeBase.objects.filter(query).order_by('-helpful_count')[:2]

        if articles:
            article = articles[0]
            return {
                'message': f"Here's what I found: 📚\n\n**{article.title}**\n\n{article.content[:400]}",
                'type': 'quick_replies',
                'replies': [
                    {'label': 'Browse Products', 'value': 'Show featured products'},
                    {'label': 'Track Order', 'value': 'Track my order'},
                ],
            }

        return {
            'message': "I want to make sure I give you the perfect answer. 🤔\n\nYou can ask me about:\n\n• **Orders** — tracking, cancellation\n• **Products** — search, recommendations\n• **Wallet** — balance, transactions\n• **Payments** — methods, EMI\n• **Returns** — policy, refunds",
            'type': 'quick_replies',
            'replies': [
                {'label': 'Track Order', 'value': 'Track my order'},
                {'label': 'Browse Products', 'value': 'Show products'},
                {'label': 'Return Policy', 'value': 'Return policy'},
                {'label': 'My Wallet', 'value': 'Show wallet'},
            ],
        }

    # ============================================================
    # MAIN ENTRY POINT — THIS WAS MISSING
    # ============================================================
    def process(self, message):
        """Main entry point — detect intent and generate response"""
        intent = self.detect_intent(message)

        handlers = {
            'track_order': self.handle_track_order,
            'return_policy': self.handle_return_policy,
            'delivery_time': self.handle_delivery_time,
            'payment_methods': self.handle_payment_methods,
            'wallet_balance': self.handle_wallet_balance,
            'product_search': self.handle_product_search,
            'order_cancel': self.handle_order_cancel,
            'coupon_promo': self.handle_coupon_promo,
            'greeting': self.handle_greeting,
            'thanks': self.handle_thanks,
            'knowledge_base': self.handle_knowledge_base,
        }

        handler = handlers.get(intent, self.handle_knowledge_base)
        try:
            response = handler(message)
        except Exception as e:
            # Never crash — always return a response
            response = {
                'message': "I apologize — I ran into a small issue. Could you rephrase your question? 🙏",
                'type': 'text',
            }

        response['intent'] = intent
        return response