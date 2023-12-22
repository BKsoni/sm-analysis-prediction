from django.http import JsonResponse
from django.shortcuts import render, redirect
import yfinance as yf
from decouple import config
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Users
from django.contrib.auth.models import User
from .utils.nlp import get_news_sentiment, get_news_feed
from .utils.Dates import calculate_extra_date
from django.core.cache import cache
import plotly.graph_objs as go
from datetime import datetime
from apis.models import Tickers
from .utils.StockData import get_stock_data

API_KEY = config("ALPHA_VANTAGE_API_KEY")

# Create your views here.
def index(request):
    url = f'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={API_KEY}'
    r = requests.get(url)
    data = r.json()
    top_gainers = []
    top_losers = []
    if data.get('top_gainers',0) and data.get('top_losers',0):
        top_gainers = [ data['top_gainers'][i] for i in range(10) ]
        top_losers = [ data['top_losers'][i] for i in range(10) ]

    return render(request, 'index.html', {
        'title': 'Home',
        'top_gainers': top_gainers,
        'top_losers': top_losers,
        'nifty_50': get_stock_data('^NSEI'),
        'nifty_bank': get_stock_data('^NSEBANK') ,
        'dowjones': get_stock_data('^DJI'),
        'nasdaq': get_stock_data('^IXIC'),
    })

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

@login_required(login_url='/login/')
def search_stock(requests):
    return render(requests, 'stock_info.html')

@login_required(login_url='/login/')
def predict(request):
    return render(request, 'predict.html')

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, "Username does not exist")
            return redirect('/login/')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Invalid Password")
            return redirect('/login/')

    return render(request, 'login.html', {"title": 'Login'})

def register_page(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('/register/')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('/register/')
        user = User.objects.create(first_name=first_name, last_name=last_name, username=username, email=email)
        user.set_password(password)
        user.save()
        messages.success(request, "Registration Successful. Please Login")
        return redirect('/login/')

    return render(request, 'register.html', {"title": 'Register'})

def logout_page(request):
    logout(request)
    return redirect('/login/')

@login_required(login_url='/login/')
def news_sentiment(request):
    # Check if the data is already cached
    output_df = cache.get('news_sentiment_data')
    news_feed = get_news_feed()
    if output_df is None:
        # If not cached, fetch and process the data
        output_df = get_news_sentiment()

        # Cache the data for future requests (adjust timeout as needed)
        cache.set('news_sentiment_data', output_df, timeout=3600)  # Cache for 1 hour (3600 seconds)

    # Render the HTML template with the data
    return render(request, 'news_sentiment.html', {'df': output_df, 'news_feed': news_feed})

@login_required(login_url='/login/')
def linear_forecast(request, ticker_symbol):
    # Assuming you are working locally with HTTP
    url = f'http://localhost:8000/api/linear-forecast/{ticker_symbol}'
    data = requests.get(url)
    tickers = Tickers.objects.all()
    # Check if the request was successful
    if data.status_code == 200:
        # You may want to parse the data if it's in a specific format (e.g., JSON)
        data_json = data.json()
        if len(data_json['seasonal_forecast']) > len(data_json['dates']):
            last_date = data_json['dates'][-1]  # Get the last date from the existing list
            num_extra_dates = len(data_json['seasonal_forecast']) - len(data_json['dates'])
            extra_dates = [calculate_extra_date(last_date, num_days=i) for i in range(1, num_extra_dates + 1)]
            data_json['dates'].extend(extra_dates)

        # Get the current date in the same format as your date data
        current_date = datetime.now().strftime('%Y-%m-%d')

        seasonal_forecast = data_json['seasonal_forecast']
        dates = data_json['dates']
        trend_forecast = data_json['trend_forecast']

        seasonal_line = go.Scatter(x=dates, y=seasonal_forecast, mode='lines+markers', name='Seasonal Forecast', line=dict(color='blue'))
        trend_line = go.Scatter(x=dates, y=trend_forecast, mode='lines+markers', name='Trend Forecast', line=dict(color='red'))

        # Find the index of the current date
        current_date_index = dates.index(current_date)

        # Create separate traces for dates before and after the current date
        seasonal_line_before = go.Scatter(x=dates[:current_date_index], y=seasonal_forecast[:current_date_index],
                                               mode='lines+markers', line=dict(color='blue'), name='Before Current Date')
        seasonal_line_after = go.Scatter(x=dates[current_date_index:], y=seasonal_forecast[current_date_index:],
                                              mode='lines+markers', line=dict(color='green'), name='After Current Date')

        chart_data = [seasonal_line_before, trend_line, seasonal_line_after]

        layout = go.Layout(title=f'Seasonal Forecast for {data_json["ticker"]} ({data_json["ticker_name"]})', xaxis_title='Time', yaxis_title='Price')

        # Render the chart_data directly to HTML using plotly.io.to_html
        chart_html = go.Figure(data=chart_data, layout=layout).to_html()

        return render(request, 'linear_regression.html', {'data': data_json, 'chart_html': chart_html, 'tickers': tickers})
    else:
        # Handle the case when the request was not successful (e.g., display an error message)
        return render(request, 'error.html', {'message': 'Failed to retrieve data'})

@login_required(login_url='/login/')
def lstm_forecast(request, ticker_symbol):
    # Assuming you are working locally with HTTP
    url = f'http://localhost:8000/api/lstm-forecast/{ticker_symbol}'
    data = requests.get(url)
    tickers = Tickers.objects.all()

    # Check if the request was successful
    if data.status_code == 200:
        # You may want to parse the data if it's in a specific format (e.g., JSON)
        data_json = data.json()

        current_date = datetime.now().strftime('%Y-%m-%d')

        prices = data_json['prices']
        dates = data_json['dates']

        prices_line = go.Scatter(x=dates, y=prices, mode='lines+markers', name='Price', line=dict(color='blue'))

        # Find the index of the current date
        current_date_index = dates.index(current_date)

        # Create separate traces for dates before and after the current date
        prices_line_before = go.Scatter(x=dates[:current_date_index], y=prices[:current_date_index],
                                               mode='lines+markers', line=dict(color='blue'), name='Before Current Date')
        prices_line_after = go.Scatter(x=dates[current_date_index:], y=prices[current_date_index:],
                                              mode='lines+markers', line=dict(color='green'), name='After Current Date')

        chart_data = [prices_line_before, prices_line_after]

        layout = go.Layout(title=f'Price Forecast for {data_json["ticker"]} ({data_json["ticker_name"]})', xaxis_title='Time', yaxis_title='Price')

        # Render the chart_data directly to HTML using plotly.io.to_html
        chart_html = go.Figure(data=chart_data, layout=layout).to_html()

        return render(request, 'lstm.html', {'data': data_json, 'chart_html': chart_html, 'tickers': tickers})
    else:
        # Handle the case when the request
        return render(request, 'error.html', {'message': 'Failed to retrieve data'})
