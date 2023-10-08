from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.LinearRegressionLib import train_model
from .models import LinearRegressionModel, Tickers
from .serializers import LinearRegressionSerializer


class TrainModelView(APIView):
    def get(self, request, ticker_symbol):
        # Your model training logic here
        # This can include loading data, training the model, and saving it
        # You can return a success response or any relevant information
        train_model(ticker_symbol)
        return Response({'message': 'Model training successful'}, status=status.HTTP_200_OK)

class TestModelView(APIView):
    queryset = LinearRegressionModel.objects.all()
    serializer_class = LinearRegressionSerializer

    def get(self, request, ticker_symbol):
        try:
            # Assuming 'ticker_symbol' is the symbol of the specific Ticker you want
            ticker_symbol = ticker_symbol.upper()
            ticker = Tickers.objects.get(ticker=ticker_symbol)
            data = self.queryset.filter(ticker=ticker).values('ticker__ticker','seasonal_forecast','dates','timestamp','trend_forecast','ticker__name')[0]
            if data:
                data['ticker'] = data.pop('ticker__ticker')
                data['ticker_name'] = data.pop('ticker__name')
                serialized_data = LinearRegressionSerializer(data).data
                return Response(serialized_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Seasonal forecast data not found for the given Ticker.'}, status=status.HTTP_404_NOT_FOUND)
        except Tickers.DoesNotExist:
            return Response({'error': 'Trained for for Ticker not found.'}, status=status.HTTP_404_NOT_FOUND)
