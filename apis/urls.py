from django.urls import path
from .views import TrainLinear, TestLinear, TrainLSTM, TestLSTM

urlpatterns = [
    path('api/train-linear/<str:ticker_symbol>', TrainLinear.as_view(), name='train-linear'),
    path('api/train-lstm/<str:ticker_symbol>', TrainLSTM.as_view(), name='train-lstm'),
    path('api/linear-forecast/<str:ticker_symbol>/', TestLinear.as_view(), name='linear-forecast'),
    path('api/lstm-forecast/<str:ticker_symbol>/', TestLSTM.as_view(), name='lstm-forecast'),
]