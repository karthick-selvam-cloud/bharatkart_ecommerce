
## 🎯 Overview

**BharatKart** is a comprehensive, production-ready e-commerce platform designed specifically for the Indian market. It combines modern web development practices with cutting-edge AI technologies to deliver a premium shopping experience.

--------------------------------------------------------------------------------------------------
### What makes it special?

- 🏛️ **Luxury Design System** — Gold/Charcoal/Ivory palette with Playfair Display typography
- 🤖 **AI Concierge** — RAG-powered chatbot using Groq/OpenRouter/Gemini LLMs
- 🧠 **ML Recommendations** — Collaborative + content-based filtering
- 💳 **Real-Time Payments** — Razorpay with UPI, cards, net banking, wallets
- 📱 **Indian Market Focus** — GST, UPI, multi-language (10+ Indian languages)
- 🎨 **Jazzmin Admin** — Custom luxury admin panel
- 🔒 **Production-Ready** — Docker, Celery, Redis, Nginx configs included

---------------------------------------------------------------------------------------------------
## 📁 Project Structure

bharatkart_ecommerce/
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not committed)
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
├── Dockerfile                      # Docker image configuration
├── docker-compose.yml              # Multi-service Docker configuration
│
├── ecommerce/                      # Django project configuration
│   ├── __init__.py
│   ├── settings.py                 # Project settings
│   ├── urls.py                     # Root URL routing
│   ├── wsgi.py                     # WSGI entry point
│   ├── asgi.py                     # ASGI entry point
│   ├── celery.py                   # Celery configuration
│   └── middleware/
│       ├── __init__.py
│       └── request_logger.py       # Request logging middleware
│
├── apps/                           # Django applications
│   │
│   ├── accounts/                   # User and account management
│   │   ├── models.py               # Users, addresses, wallets, sellers
│   │   ├── views.py                # Authentication and user dashboards
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── context_processors.py   # Global wallet information
│   │   ├── migrations/
│   │   └── templates/accounts/
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── dashboard.html
│   │       ├── wallet.html
│   │       ├── transaction_history.html
│   │       ├── my_orders.html
│   │       ├── order_detail.html
│   │       ├── profile.html
│   │       └── addresses.html
│   │
│   ├── products/                   # Product catalog
│   │   ├── models.py               # Categories, brands, products, variants
│   │   ├── views.py                # Homepage, listing, product details
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── serializers.py          # REST API serializers
│   │   ├── context_processors.py   # Global category information
│   │   ├── migrations/
│   │   └── templates/products/
│   │       ├── home.html
│   │       ├── product_list.html
│   │       └── product_detail.html
│   │
│   ├── cart/                       # Shopping cart and checkout
│   │   ├── models.py               # Cart and cart items
│   │   ├── views.py                # Add, update, remove, checkout
│   │   ├── urls.py
│   │   ├── context_processors.py   # Global cart count
│   │   ├── migrations/
│   │   └── templates/cart/
│   │       ├── cart_detail.html
│   │       └── checkout.html
│   │
│   ├── orders/                     # Order management
│   │   ├── models.py               # Orders and order items
│   │   ├── views.py                # Order list, details, cancellation
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── migrations/
│   │   └── templates/orders/
│   │       ├── order_list.html
│   │       └── order_detail.html
│   │
│   ├── payments/                   # Payment processing
│   │   ├── models.py               # Payment records
│   │   ├── views.py                # Payment, verification, webhooks
│   │   ├── razorpay_client.py      # Razorpay SDK integration
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── migrations/
│   │   └── templates/payments/
│   │       ├── payment_page.html
│   │       ├── payment_success.html
│   │       └── payment_error.html
│   │
│   ├── wishlist/                   # Wishlist management
│   │   ├── models.py               # Wishlists and wishlist items
│   │   ├── views.py                # List, toggle, remove
│   │   ├── urls.py
│   │   ├── context_processors.py   # Global wishlist count
│   │   ├── migrations/
│   │   └── templates/wishlist/
│   │       └── wishlist.html
│   │
│   └── rag/                        # AI shopping assistant
│       ├── models.py               # Knowledge base and chat history
│       ├── views.py                # Chat interface and query handling
│       ├── intent_engine.py        # User intent detection
│       ├── llm_client.py           # Groq, OpenRouter, Gemini integration
│       ├── rag_pipeline.py         # Retrieval-augmented generation
│       ├── vector_store.py         # Vector database operations
│       ├── urls.py
│       ├── admin.py
│       ├── migrations/
│       └── templates/rag/
│           └── chat.html
│
├── templates/                      # Shared HTML templates
│   ├── base_luxury.html            # Main site layout
│   ├── includes/
│   │   └── ai_support_button.html  # Floating AI assistant widget
│   ├── admin/
│   │   └── index.html              # Custom admin dashboard
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/                         # CSS, JavaScript, and images
│   ├── css/
│   │   └── admin_luxury.css
│   ├── js/
│   │   └── admin_custom.js
│   └── images/
│
├── media/                          # Uploaded media (not committed)
│   ├── products/
│   ├── categories/
│   ├── brands/
│   ├── profiles/
│   └── invoices/
│
├── scripts/                        # Data generation and maintenance
│   ├── seed_products.py
│   ├── add_product_images.py
│   ├── fix_product_images.py
│   └── generate_sample_data.py
│
├── locale/                         # Translation files
│   ├── en/LC_MESSAGES/
│   ├── hi/LC_MESSAGES/
│   └── ta/LC_MESSAGES/
│
├── docs/                           # Project documentation
│   ├── api.md
│   ├── deployment.md
│   └── architecture.md
│
├── logs/                           # Application logs (not committed)
│   ├── django.log
│   └── celery.log
│
├── faiss_index/                    # FAISS vector index (not committed)
│   └── knowledge_base.index
│
└── nginx/                          # Web server configuration
    └── nginx.conf
```
-------------------------------------------------------------
📸 Screenshots
Homepage
Luxury gold/charcoal hero section with featured products.

Product Listing
Grid of 112 products with images, ratings, and filters.

AI Concierge
Chat interface with intent detection and product cards.

Admin Panel
Custom Jazzmin theme with dark sidebar and gold accents.

Wallet
Dark luxury balance card with add money modal.


📄 License
This project is licensed under the MIT License — see LICENSE file for details.

text
MIT License

Copyright (c) 2026 BharatKart

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...

🙏 Acknowledgements

Libraries & Frameworks:
Django — The web framework for perfectionists

Django REST Framework — Powerful API toolkit

Bootstrap 5 — Frontend framework

Jazzmin — Beautiful admin theme

FAISS — Vector similarity search

Sentence Transformers — State-of-the-art embeddings

AI Services:
Groq — Lightning-fast LLM inference

Payment Services:
Razorpay — India's payment gateway

Paytm — Digital payments

PhonePe — UPI payments

Free Image Sources:
Unsplash — Beautiful free photos

Pexels — Free stock photos

Pixabay — Royalty-free images

Inspiration:
Design inspired by luxury brands like Gucci, Dior, and Chanel

Architecture inspired by Netflix, Amazon, and Flipkart

bash
git add README.md
git commit -m "docs: add comprehensive README"
git push origin main
The README is production-ready — it includes:
--------------------------------------------------------------------------
## ✨ Key Features

### 👤 User Management
| Feature | Description |
|---------|-------------|
| Multi-role accounts | Customer, Seller, Admin, Delivery Partner |
| OTP verification | Phone + Email verification |
| KYC for sellers | GST, PAN, Aadhaar validation |
| Social auth | Google, Facebook (via django-allauth) |
| Wallet system | Balance, transactions, credit/debit history |

### 🛍️ Product Catalog
| Feature | Description |
|---------|-------------|
| Hierarchical categories | MPTT tree structure (parent/child) |
| Brand management | With logos and descriptions |
| Product variants | Size, color, custom attributes |
| Multiple images | Main image + gallery (URL or upload) |
| GST calculation | Auto-calculated per product |
| Flash sales | Time-limited deals |
| Coupons | Percentage or fixed discount |
| Tags & search | Taggit + full-text search |

### 🛒 Shopping Experience
| Feature | Description |
|---------|-------------|
| Guest & user carts | Session-based or user-bound |
| Wishlist | Save products for later |
| Reviews & ratings | Verified purchase badges |
| Product recommendations | ML-powered personalized feeds |
| Recently viewed | Auto-tracked browsing history |
| Product comparison | Side-by-side specs |

### 📦 Order Management
| Feature | Description |
|---------|-------------|
| Order lifecycle | Pending → Confirmed → Shipped → Delivered |
| Real-time tracking | Courier integration ready |
| Returns & refunds | 7-day policy with workflow |
| Invoices | PDF generation |
| Order cancellation | Self-service within window |
| Email/SMS notifications | On every status change |

### 💳 Payment System
| Gateway | Status |
|---------|--------|
| Razorpay | ✅ Full integration (UPI, Cards, NetBanking, Wallets) |
| Paytm | ✅ Ready |
| PhonePe | ✅ Ready |
| Cash on Delivery | ✅ Built-in |
| Wallet payments | ✅ Instant |
| EMI | ✅ Structure ready |

### 🤖 AI & ML
| Feature | Description |
|---------|-------------|
| AI Concierge | RAG-powered chatbot |
| Intent detection | 11+ pre-built intents |
| Knowledge base | Vector search + BM25 hybrid |
| Product search | Semantic + keyword |
| Personalized recommendations | Collaborative filtering |
| Trending products | Real-time analytics |
| Order lookup | Natural language |

### 🎨 Design & UX
| Feature | Description |
|---------|-------------|
| Luxury UI | Gold/Charcoal/Ivory theme |
| Custom fonts | Playfair Display, Inter, Cormorant Garamond |
| Animations | AOS scroll animations |
| Floating AI button | Present on every page |
| Admin floating button | For staff users |
| Responsive | Mobile-first design |
| Dark luxury sections | Hero banners, CTAs |
| Jazzmin admin | Custom themed admin panel |

-----------------------------------------------------------------------
## 🏗️ Architecture

### High-Level Architecture
┌─────────────────────────────────────────────────────────────┐
│ CLIENT LAYER │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ Web │ │ Mobile │ │ Admin │ │ API │ │
│ │ Browser │ │ App │ │ Panel │ │ Clients │ │
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
│ │ │ │
┌───────▼─────────────▼─────────────▼─────────────▼───────────┐
│ LOAD BALANCER │
│ Nginx │
│ • SSL Termination • Static Files • Reverse Proxy │
└───────┬─────────────────────────────────────────────────────┘
│
┌───────▼─────────────────────────────────────────────────────┐
│ APPLICATION LAYER │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ Django + DRF + Channels │ │
│ │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │ │
│ │ │Accounts│ │Products│ │ Orders │ │Payments│ │ │
│ │ └────────┘ └────────┘ └────────┘ └────────┘ │ │
│ │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │ │
│ │ │ Cart │ │Wishlist│ │ RAG │ │ Chat │ │ │
│ │ └────────┘ └────────┘ └────────┘ └────────┘ │ │
│ └──────────────────────────────────────────────────────┘ │
└───────┬─────────────────────────────────────────────────────┘
│
┌───────▼─────────────────────────────────────────────────────┐
│ DATA LAYER │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ MySQL │ │ Redis │ │ FAISS │ │ Media │ │
│ │ (Main) │ │ (Cache) │ │ (Vectors)│ │ (S3/FS) │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────┘
│
┌───────▼─────────────────────────────────────────────────────┐
│ EXTERNAL SERVICES │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│ │Razorpay│ │ Paytm │ │ Groq │ │Twilio │ │ AWS │ │
│ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
-----------------------------------------------------------------------
### Request Flow (Payment)
User clicks "Pay"
↓

Django creates Razorpay Order via API
↓

Order ID sent to frontend
↓

Razorpay Checkout modal opens
↓

User completes payment (UPI/Card/NetBanking)
↓

Razorpay returns: {order_id, payment_id, signature}
↓

Django verifies HMAC signature
↓

Payment marked complete → Order confirmed
↓

Webhook fires (background confirmation)
↓

Email/SMS sent to user
-------------------------------------------------------------
### RAG Pipeline Flow
User Query: "Track my order ORD123ABC"
↓
┌──────────────────────────────┐
│ Intent Engine │
│ • Regex patterns │
│ • Keyword matching │
│ • 11+ intents │
└──────────┬───────────────────┘
↓
┌──────────────────────────────┐
│ Intent: track_order │
└──────────┬───────────────────┘
↓
┌──────────────────────────────┐
│ Handler dispatch │
│ → handle_track_order() │
└──────────┬───────────────────┘
↓
┌──────────────────────────────┐
│ Database query │
│ Order.objects.get(...) │
└──────────┬───────────────────┘
↓
┌──────────────────────────────┐
│ Response with rich cards │
└──────────────────────────────┘

--------------------------------------------------------------
🚀 Technologies Used
Bootstrap 5.3.2 for responsive grid

Font Awesome 6.5 for icons

Google Fonts (Playfair Display, Cormorant Garamond, Inter)

AOS 2.3.1 for scroll animations

Custom CSS with 800+ lines of luxury styling

Vanilla JavaScript for interactions
----------------------------------------------------------
## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **MySQL 8.0+**
- **Redis 7.0+** (optional, for caching/Celery)
- **Git**
- **Node.js** (optional, for linting)

### Step 1: Clone the Repository
bash

git clone https://github.com/yourusername/bharatkart.git
cd bharatkart

### Step2: Create Virtual Environment
Windows:

powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
Linux/Mac:

bash
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
bash
pip install --upgrade pip
pip install -r requirements.txt

Step 4: Setup MySQL Database
sql
CREATE DATABASE bharatkart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bharatkart_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bharatkart_db.* TO 'bharatkart_user'@'localhost';
FLUSH PRIVILEGES;

Step 5: Configure Environment
bash
cp .env.example .env
notepad .env  # Windows
nano .env     # Linux/Mac
See Environment Variables section.

Step 6: Run Migrations
bash
python manage.py makemigrations
python manage.py migrate

Step 7: Create Superuser
bash
python manage.py createsuperuser

Step 8: Seed Sample Data (Optional)
bash
# Create 112 products with images
python scripts/seed_products.py
python scripts/add_product_images.py

Step 9: Collect Static Files
bash
python manage.py collectstatic --noinput

Step 10: Run Server
bash
python manage.py runserver
