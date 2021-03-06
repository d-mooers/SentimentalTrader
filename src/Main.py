from tradingBot import TradingBot
from neuralNet.sentimentTrainer import SentimentTrainer
from neuralNet.sentimentPredictor import SentimentPredictor
from webscraping.scrapeTitles import TitleScraper
from datetime import date
from datetime import timedelta
import pandas as pd
import numpy as np
import os

def median(arrs):
    arrs.dropna(inplace=True)
    arrs.sort_values(inplace=True)
    size = len(arrs)
    return arrs.iloc[size // 2]

def main():
    scrapes_per_article = 10

    training_data_dir = '../data/'
    tickers = {
        'NKLA' : 'Nikola',
        'MSFT' : 'Microsoft',
        'AAPL' : 'Apple', 
        'NFLX' : 'Netflix',
        'WDAY' : 'Workday',
        'NVDA' : "Nvidia",
    }
    """
        'NLOK' : 'Norton',
        'XRX'  : 'Xerox',
        'HPQ'  : 'HP',
        'AMD'  : 'AMD',
        'MRNA' : 'Moderna',
        'PTON' : 'Peloton',
        'HD'   : 'Home Depot'
    }
    """

    df = pd.DataFrame(columns=['Date', 'Ticker', 'Headline'])

    for key in tickers:
        # get 20 titles for each ticker in tickers from the last 2 days
        
        ts = TitleScraper(key, tickers[key], (date.today() - timedelta(days=2)).strftime('%m/%d/%Y'), date.today().strftime('%m/%d/%Y'), scrapes_per_article)

        ts.main()
        frame = pd.DataFrame({'Date': pd.Series([date.today().strftime('%m/%d/%Y')]).repeat(len(ts.getTitleList())),
        'Ticker': pd.Series(key).repeat(len(ts.getTitleList())),
        'Headline': ts.getTitleList()})
        df = df.append(frame, ignore_index=True)

    st = SentimentTrainer()
    st.train_model(training_data_dir + 'all-data.csv')

    sp = SentimentPredictor(st)
    sp.predict_sentiment(df)

    medianPred = df.groupby('Ticker')['Prediction'].apply(median).rename('median')
    
    trader = TradingBot(tickers.keys())
    predictions = trader.analyzeStocks()
    for ticker in predictions.keys():
        result = (predictions[ticker] + (medianPred[ticker] - 0.5) * .1)
        if result > 0:
            trader.buy(ticker, int(abs(result) * 100))
        elif result < 0:
            trader.sell(ticker, int(abs(result) * 100))
        else:
            print("No change was predicted")

if __name__ == "__main__":
    main()
