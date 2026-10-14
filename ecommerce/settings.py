"""
Django Settings for BharatKart E-Commerce Platform
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-bharatkart-change-this-in-production-2024'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,0.0.0.0'
).split(',') + ['testserver']

# ============================================================
# APPLICATION DEFINITION
# ============================================================

INSTALLED_APPS = [

    'jazzmin',
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    
    # Third-party apps
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'allauth',
    'allauth.account',
    
    # Local apps
    'apps.accounts',
    'apps.products',
    'apps.cart',
    'apps.orders',
    'apps.payments',
    'apps.rag',
    'apps.wishlist',
]

# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# URLS AND TEMPLATES
# ============================================================

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'apps.accounts.context_processors.wallet',
                'apps.cart.context_processors.cart_count',   
                'apps.wishlist.context_processors.wishlist_count',
                'apps.accounts.context_processors.wallet',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'
ASGI_APPLICATION = 'ecommerce.asgi.application'

# ============================================================
# DATABASE
# ============================================================

# SQLite for development (quick start)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For MySQL (uncomment when ready for production)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.environ.get('DB_NAME', 'bharatkart_db'),
#         'USER': os.environ.get('DB_USER', 'root'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '3306'),
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#             'charset': 'utf8mb4',
#         }
#     }
# }

# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('hi', 'Hindi'),
    ('ta', 'Tamil'),
    ('te', 'Telugu'),
    ('mr', 'Marathi'),
    ('bn', 'Bengali'),
    ('gu', 'Gujarati'),
    ('kn', 'Kannada'),
    ('ml', 'Malayalam'),
    ('pa', 'Punjabi'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# ============================================================
# STATIC & MEDIA FILES
# ============================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Create static dir if it doesn't exist
STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# SITE ID
# ============================================================

SITE_ID = 1

# ============================================================
# AUTHENTICATION
# ============================================================

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'accounts:login'

AUTH_USER_MODEL = 'accounts.User'

# ============================================================
# EMAIL SETTINGS
# ============================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development

# For production, use SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# ============================================================
# CRISPY FORMS
# ============================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ============================================================
# DJANGO DEBUG TOOLBAR
# ============================================================

# ============================================================
# REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ============================================================
# CHANNELS (WebSocket)
# ============================================================

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# For production with Redis:
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [('127.0.0.1', 6379)],
#         },
#     },
# }

# ============================================================
# CELERY
# ============================================================

CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

# ============================================================
# PAYMENT GATEWAYS
# ============================================================

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', '')

PAYTM_MERCHANT_ID = os.environ.get('PAYTM_MERCHANT_ID', '')
PAYTM_MERCHANT_KEY = os.environ.get('PAYTM_MERCHANT_KEY', '')
PAYTM_WEBSITE = os.environ.get('PAYTM_WEBSITE', 'WEBSTAGING')

PHONEPE_MERCHANT_ID = os.environ.get('PHONEPE_MERCHANT_ID', '')
PHONEPE_SALT_KEY = os.environ.get('PHONEPE_SALT_KEY', '')
PHONEPE_SALT_INDEX = os.environ.get('PHONEPE_SALT_INDEX', '1')
PHONEPE_ENV = os.environ.get('PHONEPE_ENV', 'sandbox')

# ============================================================
# SMS CONFIGURATION
# ============================================================

SMS_BACKEND = os.environ.get('SMS_BACKEND', 'twilio')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

# ============================================================
# RAG / AI CONFIGURATION
# ============================================================

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
VECTOR_STORE_BACKEND = os.environ.get('VECTOR_STORE_BACKEND', 'faiss')
FAISS_INDEX_PATH = BASE_DIR / 'faiss_index' / 'knowledge_base.index'
SENTENCE_TRANSFORMER_MODEL = os.environ.get(
    'SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2'
)
RECOMMENDATION_CACHE_TIMEOUT = int(
    os.environ.get('RECOMMENDATION_CACHE_TIMEOUT', 3600)
)
MAX_RECOMMENDATIONS = int(os.environ.get('MAX_RECOMMENDATIONS', 12))

# ============================================================
# LOGGING
# ============================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ============================================================
# JAZZMIN ADMIN CONFIGURATION — Luxury Theme
# ============================================================

JAZZMIN_SETTINGS = {
    # ============ TITLE & BRANDING ============
    "site_title": "BharatKart Admin",
    "site_header": "BharatKart",
    "site_brand": "BharatKart",
    "site_logo": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Welcome to BharatKart Administration",
    "copyright": "BharatKart © 2026 · India's Premier Luxury Marketplace",
    "search_model": ["accounts.User", "products.Product", "orders.Order"],

    # ============ TOP MENU ============
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Visit Site", "url": "/", "new_window": True, "icon": "fas fa-external-link-alt"},
        {"name": "AI Concierge", "url": "/ai/chat/", "new_window": True, "icon": "fas fa-robot"},
        {"model": "accounts.User"},
        {"app": "products"},
    ],

    # ============ USER MENU ============
    "usermenu_links": [
        {"name": "My Account", "url": "/accounts/dashboard/", "new_window": False, "icon": "fas fa-user"},
        {"name": "Storefront", "url": "/", "new_window": True, "icon": "fas fa-store"},
        {"model": "auth.user"},
    ],

    # ============ SIDEBAR ============
    "show_sidebar": True,
    "navigation_expanded": False,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "accounts",
        "accounts.User",
        "accounts.Wallet",
        "accounts.WalletTransaction",
        "accounts.Address",
        "accounts.SellerProfile",
        "products",
        "products.Category",
        "products.Brand",
        "products.Product",
        "products.ProductImage",
        "products.ProductVariant",
        "orders",
        "orders.Order",
        "orders.OrderItem",
        "cart",
        "cart.Cart",
        "cart.CartItem",
        "payments",
        "payments.Payment",
        "wishlist",
        "wishlist.Wishlist",
        "rag",
        "rag.KnowledgeBase",
        "rag.ChatSession",
        "rag.ChatMessage",
    ],

    # ============ CUSTOM ICONS ============
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        
        "accounts": "fas fa-user-circle",
        "accounts.User": "fas fa-user-tie",
        "accounts.Address": "fas fa-map-marker-alt",
        "accounts.SellerProfile": "fas fa-store",
        "accounts.Wallet": "fas fa-wallet",
        "accounts.WalletTransaction": "fas fa-exchange-alt",
        
        "products": "fas fa-box",
        "products.Category": "fas fa-tags",
        "products.Brand": "fas fa-crown",
        "products.Product": "fas fa-cube",
        "products.ProductImage": "fas fa-images",
        "products.ProductVariant": "fas fa-layer-group",
        
        "orders": "fas fa-shopping-cart",
        "orders.Order": "fas fa-receipt",
        "orders.OrderItem": "fas fa-box-open",
        
        "cart": "fas fa-shopping-bag",
        "cart.Cart": "fas fa-shopping-bag",
        "cart.CartItem": "fas fa-cart-plus",
        
        "payments": "fas fa-credit-card",
        "payments.Payment": "fas fa-money-check-alt",
        
        "wishlist": "fas fa-heart",
        "wishlist.Wishlist": "fas fa-heart",
        
        "rag": "fas fa-robot",
        "rag.KnowledgeBase": "fas fa-book",
        "rag.ChatSession": "fas fa-comments",
        "rag.ChatMessage": "fas fa-comment-dots",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # ============ UI CUSTOMIZATION ============
    "related_modal_active": True,
    "custom_css": "css/admin_luxury.css",
    "custom_js": "js/admin_custom.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,

    # ============ UI TWEAKS ============
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    "language_chooser": False,
}


# ============================================================
# JAZZMIN UI TWEAKS — Luxury Gold/Charcoal Theme
# ============================================================

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-gold",
    "navbar": "navbar-dark navbar-charcoal",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-charcoal",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# Create logs directory if it doesn't exist
(BASE_DIR / 'logs').mkdir(exist_ok=True)
AUTH_USER_MODEL = 'accounts.User'

GROQ_API_KEY = config('GROQ_API_KEY', default='')

AI_PROVIDER = config('AI_PROVIDER', default='groq')

AI_FALLBACK_ORDER = ['groq', 'openrouter', 'gemini', 'template']