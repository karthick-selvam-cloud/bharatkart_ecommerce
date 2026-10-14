from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_detail, name='detail'),        # ← wishlist:detail
    path('toggle/<int:product_id>/', views.toggle, name='toggle'),
    path('remove/<int:item_id>/', views.remove, name='remove'),
]