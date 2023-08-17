from django.shortcuts import render
from yahoo_fin.stock_info import *
import yfinance as yf
from django.http import HttpResponse
import time
from threading import Thread
import queue

# Simple Functions
def extract_stock_info(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d", interval='1m')
    # print(data)
    if data.empty:
        return None

    latest_price = data['Close'].iloc[-1]
    open_price = data['Open'].iloc[0]
    high_price = data['High'].max()
    low_price = data['Low'].min()
    previous_close = data['Close'].iloc[-2]
    volume = stock.info['volume']
    market_cap = stock.info['marketCap']


    return {
        'Latest Price': "{:.2f}".format(latest_price),
        'Previous Close': "{:.2f}".format(previous_close),
        'Open Price': "{:.2f}".format(open_price),
        'High Price': "{:.2f}".format(high_price),
        'Low Price': "{:.2f}".format(low_price),
        'Volume': "{:.2f}".format(volume),
        'Market Cap': "{:.2f}".format(market_cap),
    }
# Create your views here.
def stockPicker(request):
    stock_picker = tickers_nifty50()
    return render(request, 'stockpicker.html', {'stock_picker':stock_picker} )

def stockTracker(request):
    # symbol = 'RELIANCE.NS'
    # stock = fetch_stock_data(symbol)
    # stock_info = extract_stock_info(stock)
    # print(stock_info)
    stock_selected = request.GET.getlist('stockpicker')
    available_stocks = tickers_nifty50()
    data = {}
    # for i in stock_selected:
    #     if i in available_stocks:
    #         symbol = i
    #         stock_info = extract_stock_info(symbol)
    #         data[i] = stock_info
    #     else:
    #         HttpResponse("Stock not available")
    # print(data)

    available_stocks = tickers_nifty50()
    for i in stock_selected:
        if i in available_stocks:
            pass
        else:
            return HttpResponse("Error")

    n_threads = len(stock_selected)
    thread_list = []
    que = queue.Queue()
    start = time.time()

    for i in range(n_threads):
        thread = Thread(target = lambda q, arg1: q.put({stock_selected[i]: extract_stock_info(arg1)}), args = (que, stock_selected[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)
    end = time.time()
    time_taken =  end - start

    # print(data)

    return render(request, 'stocktracker.html', {'data':data, 'stock_selected':", ".join(stock_selected)})