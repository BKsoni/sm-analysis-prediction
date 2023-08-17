from django.http import JsonResponse
from django.shortcuts import render
import yfinance as yf

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def autocomplete(request):
    search_text = request.GET.get('search', '')
    all_tickers = yf.Tickers().tickers
    print(all_tickers)
    suggestions = [ticker.info['symbol'] for ticker in all_tickers]
    yf.set_tz_cache_location("custom/cache/location")
    filtered_suggestions = [suggestion for suggestion in suggestions if search_text in suggestion]

    return JsonResponse({'suggestions': filtered_suggestions})

def search_stock(requests):
    return render(requests, 'stock_info.html')