from django.urls import path
from .views import trade_items

urlpatterns = [
    path('trade/', trade_items, name='trade-items'),
]
