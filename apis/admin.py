from django.contrib import admin
from .models import Tickers, LinearRegressionModel

# Register your models here.
class TickersAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'is_active')
    list_filter = ('ticker', 'name', 'is_active')
    search_fields = ('ticker', 'name', 'is_active')
    ordering = ('ticker', 'name', 'is_active')

class LinearRegressionModelAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'timestamp','trend_forecast', 'seasonal_forecast')
    list_filter = ('ticker', 'timestamp','trend_forecast', 'seasonal_forecast')
    search_fields = ('ticker', 'timestamp','trend_forecast', 'seasonal_forecast')
    ordering = ('ticker', 'timestamp','trend_forecast', 'seasonal_forecast')

admin.site.register(Tickers, TickersAdmin)
admin.site.register(LinearRegressionModel, LinearRegressionModelAdmin)
