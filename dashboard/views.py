# views.py
import yfinance as yf
import plotly.graph_objs as go
from django.shortcuts import render
from django.contrib import messages

def fetch_stock_data(symbol, duration):
    try:
        if duration=="1d":
            stock_data = yf.download(symbol, interval='1m', period=duration)  # 1d data
        else:
            stock_data = yf.download(symbol, period=duration)  # Fetch data by period
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

def stock_info(request):
    search_text = request.GET.get('ticker', '')

    if not search_text:
        messages.info(request, 'Please enter a stock ticker.')
        return render(request, 'stock_info.html')
    symbol = search_text.upper()
    duration = '1d'

    stock_data = fetch_stock_data(symbol, duration)
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

    return render(request, 'stock_info.html', {'chart': chart.to_html()})
