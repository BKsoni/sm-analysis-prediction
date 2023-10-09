from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.LinearRegressionLib import train_model
from .utils.LSTM import train_lstm_model
from .models import LinearRegressionModel, Tickers, LSTMModel
from .serializers import LinearModelSerializer, LSTMModelSerializer


class TrainLinear(APIView):
    def get(self, request, ticker_symbol):
        train_model(ticker_symbol)
        return Response({'message': 'Model training successful'}, status=status.HTTP_200_OK)

class TrainLSTM(APIView):
    def get(self, request, ticker_symbol):
        # Your model training logic here
        # This can include loading data, training the model, and saving it
        # You can return a success response or any relevant information
        train_lstm_model(ticker_symbol)
        return Response({'message': 'Model training successful'}, status=status.HTTP_200_OK)

class TestLinear(APIView):
    queryset = LinearRegressionModel.objects.all()
    serializer_class = LinearModelSerializer

    def get(self, request, ticker_symbol):
        try:
            # Assuming 'ticker_symbol' is the symbol of the specific Ticker you want
            ticker_symbol = ticker_symbol.upper()
            ticker = Tickers.objects.get(ticker=ticker_symbol)
            data = self.queryset.filter(ticker=ticker).values('ticker__ticker','seasonal_forecast','dates','timestamp','trend_forecast','ticker__name')[0]
            if data:
                data['ticker'] = data.pop('ticker__ticker')
                data['ticker_name'] = data.pop('ticker__name')
                serialized_data = LinearModelSerializer(data).data
                return Response(serialized_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Seasonal forecast data not found for the given Ticker.'}, status=status.HTTP_404_NOT_FOUND)
        except Tickers.DoesNotExist:
            return Response({'error': 'Trained for for Ticker not found.'}, status=status.HTTP_404_NOT_FOUND)

class TestLSTM(APIView):
    queryset = LSTMModel.objects.all()
    serializer_class = LSTMModelSerializer

    def get(self, request, ticker_symbol):
        try:
            # Assuming 'ticker_symbol' is the symbol of the specific Ticker you want
            ticker_symbol = ticker_symbol.upper()
            ticker = Tickers.objects.get(ticker=ticker_symbol)
            data = self.queryset.filter(ticker=ticker).values('ticker__ticker','prices','dates','timestamp','ticker__name')[0]
            if data:
                data['ticker'] = data.pop('ticker__ticker')
                data['ticker_name'] = data.pop('ticker__name')
                serialized_data = LSTMModelSerializer(data).data
                return Response(serialized_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Forecast data not found for the given Ticker.'}, status=status.HTTP_404_NOT_FOUND)
        except Tickers.DoesNotExist:
            return Response({'error': 'Trained for for Ticker not found.'}, status=status.HTTP_404_NOT_FOUND)