
from django.urls import path
from .views import stock_info,get_news

urlpatterns = [
    path('searchstock/', stock_info, name='stock_info'),
    path('news/', get_news, name='news')
]