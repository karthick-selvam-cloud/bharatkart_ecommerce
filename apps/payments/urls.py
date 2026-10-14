from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:order_id>/', views.payment_page, name='page'),
    path('success/<int:order_id>/', views.payment_success, name='success'),
    path('error/', views.payment_error, name='error'),
]