
from django.urls import path
from .views import stock_info

urlpatterns = [
    path('searchstock/', stock_info, name='stock_info'),
]