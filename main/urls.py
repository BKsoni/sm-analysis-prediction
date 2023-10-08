from django.urls import path, include
from .views import index, about,autocomplete, predict, login_page, register_page, logout_page, news_sentiment, linear_forecast

urlpatterns = [
    path("", index, name="index"),
    path("about/", about, name="about"),
    path('autocomplete/', autocomplete, name='autocomplete'),
    path('predict/', predict, name='predict'),
    path('predict/news-sentiment/', news_sentiment, name='news_sentiment'),
    path('predict/linear-forecast/<str:ticker_symbol>/', linear_forecast, name='linear-forecast'),
    path("login/", login_page),
    path("register/", register_page),
    path("logout/", logout_page),
    path("", include("apis.urls")),
]