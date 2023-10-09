import requests
from bs4 import BeautifulSoup
import spacy
import pandas as pd
import yfinance as yf

nlp = spacy.load("en_core_web_sm")

def extract_text_from_rss():
    """
    Extracts text from RSS feed
    """
    #https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms
    #https://www.moneycontrol.com/rss/buzzingstocks.xml
    r = requests.get("https://www.moneycontrol.com/rss/buzzingstocks.xml")
    soup = BeautifulSoup(r.content,features='xml')
    headlines = soup.findAll('title')
    return headlines

def get_news_feed():
    """
    Returns news feed
    """
    headings = extract_text_from_rss()
    feeds = [heading.text for heading in headings]
    return feeds

def get_news_sentiment():
    """
    Returns news sentiment
    """
    stock_info_dict={
        'Org':[],
        'Symbol':[],
        'currentPrice':[],
        'dayHigh':[],
        'dayLow':[]
        # 'forwardPE':[],
        # 'dividendYield':[]
    }
    headings = extract_text_from_rss()

    stocks_df = pd.read_csv("./data/ind_nifty500list.csv")

    for title in headings:
        doc = nlp(title.text)
        for ent in doc.ents:
            try:
                if stocks_df['Company Name'].str.contains(ent.text).sum():
                    symbol = stocks_df[stocks_df['Company Name'].str.\
                        contains(ent.text)]['Symbol'].values[0]
                    org_name = stocks_df[stocks_df['Company Name'].str.\
                        contains(ent.text)]['Company Name'].values[0]

                    stock_info = yf.Ticker(symbol+".NS").info

                    stock_info_dict['Org'].append(org_name)
                    stock_info_dict['Symbol'].append(symbol)
                    stock_info_dict['currentPrice'].append(stock_info['currentPrice'])
                    stock_info_dict['dayHigh'].append(stock_info['dayHigh'])
                    stock_info_dict['dayLow'].append(stock_info['dayLow'])
                    # stock_info_dict['forwardPE'].append(stock_info['forwardPE'])
                    # stock_info_dict['dividendYield'].append(stock_info['dividendYield'])
                else:
                    pass
            except:
                pass

    # remove duplicates from stock_info_df
    stock_info_df = pd.DataFrame(stock_info_dict)
    stock_info_df.drop_duplicates(inplace=True)
    return stock_info_df
