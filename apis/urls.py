from django.urls import path
from .views import TrainModelView, TestModelView

urlpatterns = [
    path('train/<str:ticker_symbol>', TrainModelView.as_view(), name='train-model'),
    path('api/linear-forecast/<str:ticker_symbol>/', TestModelView.as_view(), name='linear-forecast'),
]