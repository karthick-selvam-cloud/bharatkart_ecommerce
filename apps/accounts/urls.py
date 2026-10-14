"""
Account URLs for BharatKart
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('addresses/', views.addresses_view, name='addresses'),
    
    # Wallet (updated)
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/add-money/', views.add_money_view, name='add_money'),
    path('wallet/transactions/', views.transaction_history_view, name='transaction_history'),
    
    # Orders
    path('orders/', views.my_orders_view, name='my_orders'),
    path('orders/<int:order_id>/', views.account_order_detail_view, name='order_detail'),
    path('orders/<int:order_id>/cancel/', views.cancel_order_view, name='cancel_order'),

    # Addresses
    path('addresses/', views.addresses_view, name='addresses'),
    path('addresses/<int:address_id>/set-default/', views.set_default_address_view, name='set_default_address'),
    path('addresses/<int:address_id>/delete/', views.delete_address_view, name='delete_address'),
]