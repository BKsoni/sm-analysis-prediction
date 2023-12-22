import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd

def getTickerData(SYMBOL="RELIANCE.NS"):
    print("Training started (Linear Model)")
    current_date = datetime.date.today()
    startDate = datetime.datetime(current_date.year-2, current_date.month,current_date.day)
    endDate = datetime.datetime(current_date.year,current_date.month, current_date.day)
    ticker = yf.download(SYMBOL, start=startDate, end=endDate)
    print("Training completed (Linear Model)")
    return ticker, SYMBOL