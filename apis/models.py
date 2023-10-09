from django.db import models

# Create your models here.
class Tickers(models.Model):
    ticker = models.CharField(max_length=100)
    name = models.CharField(max_length=100,default="")
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.ticker

class LinearRegressionModel(models.Model):
    ticker = models.ForeignKey(Tickers, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    dates = models.JSONField(null=True, blank=True)
    trend_forecast = models.JSONField(null=True, blank=True)
    seasonal_forecast = models.JSONField(null=True, blank=True)
    def __str__(self):
        return self.ticker.ticker

class LSTMModel(models.Model):
    ticker = models.ForeignKey(Tickers, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    dates = models.JSONField(null=True, blank=True)
    prices = models.JSONField(null=True, blank=True)
    def __str__(self):
        return self.ticker.ticker
