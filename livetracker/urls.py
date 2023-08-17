from django.contrib import admin
from django.urls import path, include
from livetracker.views import stockPicker, stockTracker

urlpatterns = [

    path('stockpicker/',stockPicker, name='stockPicker'),
    path('stocktracker/', stockTracker, name='stockTracker'),
]