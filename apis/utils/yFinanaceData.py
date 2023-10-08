import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pandas as pd

def getTickerData(SYMBOL="RELIANCE.NS"):
    current_date = datetime.date.today()
    startDate = datetime.datetime(current_date.year-2, current_date.month,current_date.day)
    endDate = datetime.datetime(current_date.year,current_date.month, current_date.day)
    ticker = yf.Ticker(SYMBOL)
    name = ticker.info['shortName']
    ticker = pd.DataFrame(ticker.history(start=startDate,end=endDate))
    return ticker, name