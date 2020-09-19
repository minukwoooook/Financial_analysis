import pandas as pd
import Analyzer
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from mpl_finance import candlestick_ohlc

class StochasticAnalyzer:
    def __init__(self, code, start_date, end_date):
        self.mk = Analyzer.MarketDB()
        self.df = self.mk.get_daily_price(code, start_date, end_date)
        print("Get {} stock info for Stochastic : date: {} ~ {}".format(code, start_date, end_date))
        print(self.df)
    def backtest(self, day1=None, day2=None, day3=None):
        #day1 for fast %K, day2 for fast %D(slow %K), day3 for slow %D
        if day1 is None:
            day1 = 5
        if day2 is None:
            day2 = 3
        if day3 is None:
            day3 = 3
        self.df['high_max'] = self.df['high'].rolling(window=day1).max()
        self.df['low_min'] = self.df['low'].rolling(window=day1).min()
        #self.df = self.df.dropna()
        self.df['fast_%K'] = (self.df['close']-self.df['low_min']) / (self.df['high_max']-self.df['low_min']) * 100
        self.df['slow_%K'] = self.df['fast_%K'].ewm(span=day2).mean()
        self.df['slow_%D'] = self.df['slow_%K'].ewm(span=day3).mean()
        ''' add bollinger band'''
        self.df['MA20'] = self.df['close'].rolling(window=20).mean()
        self.df['stddev'] = self.df['close'].rolling(window=20).std()
        self.df['upper'] = self.df['MA20'] + 2 * self.df['stddev']
        self.df['lower'] = self.df['MA20'] - 2 * self.df['stddev']
        self.df['PB'] = (self.df['close'] - self.df['lower']) / (self.df['upper'] - self.df['lower'])
        self.df['II'] = (2*self.df['close']-self.df['high']-self.df['low'])/(self.df['high']-self.df['low'])*self.df['volume']
        self.df['IIP21'] = self.df['II'].rolling(window=21).sum()/self.df['volume'].rolling(window=21).sum()*100
        self.df = self.df.dropna()
        ''' to here'''
        flag = 0
        buy_date = []
        buy_price = []
        sell_date = []
        sell_price = []
        for i in range(1, len(self.df['close'])-1):
            if (self.df['slow_%K'].values[i-1] < self.df['slow_%D'].values[i-1]) and \
                    (self.df['slow_%K'].values[i] > self.df['slow_%D'].values[i]) and \
                    (self.df['PB'].values[i] < 0.05):
                    #(self.df['PB'].values[i] < 0.3) and (self.df['IIP21'].values[i] > 0):
                if flag == 0:
                    flag = 1
                    buy_date.append(self.df['date'].values[i + 1])
                    buy_price.append(self.df['open'].values[i + 1])
            #elif ((self.df['slow_%K'].values[i-1] > self.df['slow_%D'].values[i-1]) and \
            #        (self.df['slow_%K'].values[i] < self.df['slow_%D'].values[i])) or \
            #        self.df['PB'].values[i] > 1:
            elif self.df['slow_%K'].values[i] > 80 or self.df['PB'].values[i] > 1:
                if flag == 1:
                    flag = 0
                    sell_price.append(self.df['open'].values[i + 1])
                    sell_date.append(self.df['date'].values[i + 1])
        trade_df = pd.DataFrame(
            {'buy_date': buy_date, 'buy_price': buy_price, 'sell_date': sell_date, 'sell_price': sell_price})
        trade_df['earn'] = trade_df['sell_price'] - trade_df['buy_price']
        trade_df['rate_of_return'] = (trade_df['sell_price'] - trade_df['buy_price']) / trade_df['buy_price'] * 100
        print(trade_df['rate_of_return'].mean())
        print(trade_df)