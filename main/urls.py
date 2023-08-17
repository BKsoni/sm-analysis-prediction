from django.urls import path
from .views import index, about,autocomplete, search_stock
urlpatterns = [
    path("", index, name="index"),
    path("about/", about, name="about"),
    path('autocomplete/', autocomplete, name='autocomplete'),
]