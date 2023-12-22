import yfinance as yf

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")  # You can adjust the period as needed

    if not data.empty:
        latest_price = data['Close'].iloc[-1]
        change = latest_price - data['Open'].iloc[-1]
        change_percent = (change / data['Open'].iloc[-1]) * 100

        return {
            'latest_price': latest_price,
            'change': change,
            'change_percent': change_percent
        }
    else:
        return None