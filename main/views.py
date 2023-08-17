from django.http import JsonResponse
from django.shortcuts import render
import yfinance as yf
from decouple import config
import requests

API_KEY = config("ALPHA_VANTAGE_API_KEY")


# Create your views here.
def index(request):
    url = 'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=XWN6DUC5D5WU2L9Q'
    r = requests.get(url)
    data = r.json()
    top_gainers = [ data['top_gainers'][i] for i in range(10) ]
    top_losers = [ data['top_losers'][i] for i in range(10) ]
    return render(request, 'index.html', {'title': 'Home', 'top_gainers': top_gainers, 'top_losers': top_losers})

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