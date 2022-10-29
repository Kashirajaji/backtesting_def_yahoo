#!/usr/bin/env python
# coding: utf-8

# In[1]:


import yfinance as yf
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


# In[2]:


class Backtest:
    def __init__ (self, symbol):
        self.symbol = symbol
        self.df =  yf.download (self.symbol,start = "2018-01-01")
        if self.df.empty:
            print("No data pulled")
        else:
            self.calc_indicators()
            self.generate_signals()
            self.loop_int()
            self.profit = self.calc_profit()
            self.max_dd = self.profit.min()
            self.acum_profit = self.profit.sum()
            
    def calc_indicators(self):
        self.df["SMA_100"] = self.df.Close.rolling(100).mean()
        self.df["SMA_20"] = self.df.Close.rolling(20).mean()
        self.df["stddev"]= self.df.Close.rolling(20).std()
        self.df["bb_Upper"]= self.df.SMA_20 + (2 * self.df.stddev)
        self.df["bb_Lower"] = self.df.SMA_20 - (2 * self.df.stddev)
        self.df ["rsi"] = ta.momentum.rsi(self.df.Close,window=6)
        self.df.dropna(inplace=True)
      
        
    def generate_signals (self):
        conditions = [(self.df.SMA_100<self.df.Close)& (self.df.rsi<30)&(self.df.Close < self.df.bb_Lower),
                     (self.df.rsi>70)&(self.df.Close > self.df.bb_Upper)]
        
        choices = ["Buy", "Sell"]
        
        self.df["signal"] =  np.select ( conditions, choices)
        
        self.df.signal = self.df.signal.shift()
        self.df.dropna(inplace=True)
        
    def loop_int(self):
        position =  False
        buydates, selldates = [], []
        buyproces, sellprices = [], []
        
        for index, row in self.df.iterrows():
            if not position and row ["signal"] == "Buy":
                position = True
                buydates.append(index)
         
                
            if position and row ["signal"] == "Sell":
                position = False
                selldates.append(index)
        self.buy_arr = self.df.loc[buydates].Open
        self.sell_arr = self.df.loc[selldates].Open
        
    def calc_profit(self):
        if self.buy_arr.index[-1]> self.sell_arr.index[-1]:
            self.buy_arr = self.buy_arr[:-1]
        return (self.sell_arr.values - self.buy_arr.values) / self.buy_arr.values
    
    def plot_chart (self):
        plt.figure(figsize=(10,5))
        plt.plot(self.df.Close)
        plt.scatter(self.buy_arr.index, self.buy_arr.values, marker ="^", c = "g")
        plt.scatter (self.sell_arr.index, self.sell_arr.values, marker = "v", c="r")


# In[3]:


instance = Backtest("MELI")


# In[4]:


instance


# In[5]:


instance.profit


# In[6]:


instance.plot_chart()


# In[7]:


tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0].Symbol


# In[8]:


tickers


# In[9]:


t_changes = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[1]
t_changes


# In[10]:


added = t_changes[pd.to_datetime(t_changes.Date.Date)>="2019-01-01"].Added
removed = t_changes[pd.to_datetime(t_changes.Date.Date)>="2019-01-01"].Removed
removed


# In[11]:


tickers = tickers[~(tickers.isin(added.Ticker))]
tickers


# In[12]:


removed.iloc[0].Ticker = "UAA"


# In[13]:


tickers = tickers.append(removed.Ticker)


# In[14]:


tickers.dropna(inplace=True)


# In[15]:


tickers.drop_duplicates(inplace=True)


# In[16]:


tickers.reset_index(drop=True)


# In[17]:


instances = []


for ticker in tickers:
    instances.append(Backtest(ticker))


# In[20]:


profits, comp_name = [], []

for obj in instances:
    if not obj.df.empty:
        profits.append(obj.profit.sum())
        comp_name.append(obj.symbol)
        


# In[21]:


ret_frame = pd.DataFrame (profits, index = comp_name, columns = ["cumul_ret"])


# In[22]:


ret_frame= ret_frame.sort_values("cumul_ret",ascending=False)
ret_frame.to_csv("resultado_spy500_bullinger.csv")
ret_frame


# In[23]:


tickers[tickers=="EXPE"]


# In[24]:


instances[187].plot_chart()


# In[25]:


instances[187].profit.sum()


# In[31]:


POSITIVAS = ret_frame["cumul_ret"]>0
POSITIVAS = ret_frame[POSITIVAS]
NEGATIVAS = ret_frame["cumul_ret"]<0
NEGATIVAS = ret_frame[NEGATIVAS]


# In[32]:


POSITIVAS.count()


# In[33]:


NEGATIVAS.count()


# In[ ]:




