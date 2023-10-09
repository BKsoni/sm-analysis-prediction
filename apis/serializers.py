from rest_framework import serializers

class LinearModelSerializer(serializers.Serializer):
    ticker = serializers.CharField()
    seasonal_forecast = serializers.JSONField()
    trend_forecast = serializers.JSONField()
    dates = serializers.JSONField()
    timestamp = serializers.DateTimeField()
    ticker_name = serializers.CharField()
    class Meta:
        fields = ('ticker', 'ticker_name', 'seasonal_forecast', 'trend_forecast', 'timestamp')

class LSTMModelSerializer(serializers.Serializer):
    ticker = serializers.CharField()
    dates = serializers.JSONField()
    prices = serializers.JSONField()
    timestamp = serializers.DateTimeField()
    ticker_name = serializers.CharField()
    class Meta:
        fields = ('ticker', 'ticker_name', 'dates', 'prices', 'timestamp')