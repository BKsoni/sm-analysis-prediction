# views.py
import yfinance as yf
import plotly.graph_objs as go
from django.shortcuts import render
from django.contrib import messages
from decouple import config
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

API_KEY = config("ALPHA_VANTAGE_API_KEY")

def fetch_stock_data(symbol,duration):
    try:
        if duration=="live":
            stock_data = yf.download(symbol, period="1d", interval="1m")  # Fetch data by period
        else:
            stock_data = yf.download(symbol)
    except Exception as e:
        print("stock_data error")

    stock_data['MA5'] = stock_data['Close'].rolling(5).mean()
    stock_data['MA20'] = stock_data['Close'].rolling(20).mean()
    stock_data['Exponential MA5'] = stock_data['Close'].ewm(span=5, adjust=False).mean()
    # stock_data['RSI'] = 100 - (100 / (1 + (stock_data['Close'] - stock_data['Close'].shift(1)) / (stock_data['Close'].shift(1) - stock_data['Close'].shift(2))))
    # stock_data['MACD'] = stock_data['Close'].ewm(span=12, adjust=False).mean() - stock_data['Close'].ewm(span=26, adjust=False).mean()
    stock_data['Exponential MA8'] = stock_data['Close'].ewm(span=8, adjust=False).mean()
    stock_data['Exponential MA13'] = stock_data['Close'].ewm(span=13, adjust=False).mean()
    stock_data['SuperTrend'] = stock_data['Close'].rolling(7).mean() + (stock_data['Close'].rolling(7).std() * 3)

    return stock_data

@login_required(login_url='/login/')
def stock_info(request):

    search_text = request.GET.get('ticker', '')

    if not search_text:
        messages.info(request, 'Please enter a stock ticker.')
        return render(request, 'stock_info.html')
    symbol = search_text.upper()
    duration = request.GET.get('duration', 'live')  # Default to 'live'

    stock_data = fetch_stock_data(symbol,duration)
    if stock_data.empty:
        messages.error(request, f'Error fetching data for {symbol}. Please try again.')
        return render(request, 'stock_info.html')

    dates = stock_data.index
    opening_prices = stock_data['Open']
    closing_prices = stock_data['Close']
    highest_prices = stock_data['High']
    lowest_prices = stock_data['Low']

    candlestick_trace = go.Candlestick(x=dates, open=opening_prices, high=highest_prices, low=lowest_prices, close=closing_prices, name=symbol)
    line_chart = go.Scatter(x=dates, y=closing_prices, mode='lines+markers', name=symbol, line=dict(color='black'))

    scatter_MA5 = go.Scatter(x=dates, y=stock_data['MA5'], mode='lines', name='MA5', line=dict(color='blue'))
    scatter_MA20 = go.Scatter(x=dates, y=stock_data['MA20'], mode='lines', name='MA20', line=dict(color='orange'))
    scatter_Exponential_MA5 = go.Scatter(x=dates, y=stock_data['Exponential MA5'], mode='lines', name='Exponential MA5', line=dict(color='green'))
    scatter_Exponential_MA8 = go.Scatter(x=dates, y=stock_data['Exponential MA8'], mode='lines', name='Exponential MA8', line=dict(color='red'))
    scatter_Exponential_MA13 = go.Scatter(x=dates, y=stock_data['Exponential MA13'], mode='lines', name='Exponential MA13', line=dict(color='purple'))
    # rsi = go.Scatter(x=dates, y=stock_data['RSI'], mode='lines', name='RSI', line=dict(color='red'))
    # macd = go.Scatter(x=dates, y=stock_data['MACD'], mode='lines', name='MACD', line=dict(color='purple'))
    super_trend = go.Scatter(x=dates, y=stock_data['SuperTrend'], mode='lines', name='SuperTrend', line=dict(color='brown'))

    # Set visibility to False for all traces by default
    for trace in [candlestick_trace, line_chart, scatter_MA5, scatter_MA20, scatter_Exponential_MA5,scatter_Exponential_MA8,scatter_Exponential_MA13,super_trend]:
        trace.visible = False

    # Set visibility to True only for the selected default chart (candlestick or line chart)
    default_chart_trace = candlestick_trace  # Change this to line_chart if you want line chart as default
    default_chart_trace.visible = True

    chart_data = [candlestick_trace, line_chart, scatter_MA5, scatter_MA20, scatter_Exponential_MA5, scatter_Exponential_MA8,scatter_Exponential_MA13, super_trend]

    layout = go.Layout(
    title=f'{symbol} Stock Chart',
    xaxis=dict(title='Date'),
    yaxis=dict(title='Closing Price'),
    autosize=True,
    width=1500,
    height=800,
    updatemenus=[
        {
            'buttons': [

                {'args': [{'visible': [True, False, True, True, True, True, True]}, {'title': f'{symbol} Stock Chart'}],
                 'label': 'Candlestick',
                 'method': 'update'},
                {'args': [{'visible': [False, True, True, True, True, True, True]}, {'title': f'{symbol} Stock Chart'}],
                 'label': 'LineChart',
                 'method': 'update'},
            ],
            'direction': 'down',
            'showactive': False,
        }
    ],
    )


    chart = go.Figure(data=chart_data, layout=layout)
    if duration == "past":
        chart.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=5, label="5d", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        chart.update_layout(xaxis_rangeslider_visible=True)

        if request.GET.get('duration') == "5d":
            # Update the y-axis range based on 5 days data
            min_price = min(closing_prices[-5:])
            max_price = max(closing_prices[-5:])
            chart.update_yaxes(range=[min_price, max_price])

        chart.update_yaxes(fixedrange=True)

    return render(request, 'stock_info.html', {'chart': chart.to_html()})

@login_required(login_url='/login/')
def get_news(request):
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey={API_KEY}'
    r = requests.get(url)
    data = r.json()
    page_obj = None
    if data.get('feed',0):
        news = data['feed']
        paginator = Paginator(news, 6)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
    return render(request, 'news.html', {'title': 'News','news_list': page_obj})
