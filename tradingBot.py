#Imports
import ibapi
from concurrent.futures.process import EXTRA_QUEUED_CALLS
from symtable import Symbol
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import numpy as np
import pandas as pd
import ta
import pytz
import math
from OrderSamples import OrderSamples
from datetime import datetime, timedelta
from ibapi.contract import Contract
from ibapi.order import *
import threading
import time

#Vars
orderId = 1
#Class for connnecting to IBKR
class IBApi(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
    #Get historical data (if bot starts late) / Historical Backtest Data
    def historicalData(self, reqId, bar):
        try: 
            bot.on_bar_update(reqId, bar, False)
        except Exception as e:
            print(e)
    
    #On Realtime Bar after historical data finishes
    def historicalDataUpdate(self, reqId, bar):
        try: 
            bot.on_bar_update(reqId, bar, True)
        except Exception as e:
            print(e)
    #On Historical data ends
    def historicalDataEnd(self, reqId, start, end):
        print(reqId)

    #Get next order ID
    def nextValidId(self, nextorderId):
        global orderId
        orderId = nextorderId

    #Listen for realtimeBars
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        super().reqRealTimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        try:
            bot.on_bar_update(reqId, time, open_, high, low, close, volume, wap, count)
        except Exception as e:
            print(e)
        
        def error(self, id, errorCode, errorMsg):
            print(errorCode)
            print(errorMsg)


#Bar Object
class Bar:
    open = 0
    low = 0
    high = 0
    close = 0 
    volume = 0
    date = datetime.now()
    def __init__(self):
        self.open = 0
        self.low = 0
        self.high = 0
        self.close = 0
        self.volume = 0
        self.date = datetime.now()



#Bot Logic
class Bot:
    ib = None
    barsize = 60
    currentBar = Bar()
    bars = []
    reqId = 1
    global orderId
    ema1Period = 9
    ema2Period = 21
    symbol = ""
    initalbartime = datetime.now().astimezone(pytz.timezone("America/New_York"))


    def __init__(self):
        #Connect to IBKR on init
        self.ib = IBApi()
        self.ib.connect("127.0.0.1", 7496, 1)
    
        #threading
        ib_thread = threading.Thread(target=self.run_loop, daemon=True)
        ib_thread.start()
        time.sleep(1)

        currentBar = Bar()




        #Get Symbol/Ticker
        self.symbol = input("Enter the symbol/ticker you want to trade: ")

        #Get bar size
        self.barsize = input("Enter the barsize you want to trade in minutes: ")
        mintext = " min"
        if (int(self.barsize) > 1):
            mintext = " mins"
        
        queryTime = (datetime.now().astimezone(pytz.timezone("America/New_York"))-timedelta(days=1)).replace(hour=16,minute=0,second=0,microsecond=0).strftime("%Y%m%d %H:%M:%S")


        #Create contract/Stock object to store stock info
        contract = Contract()
        contract.symbol = self.symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        #Request Market Data
        #self.ib.reqRealTimeBars(0, contract, 3600, "MIDPOINT", 1, []) # 1 = Regular Trading Hours - 0 = all trading hours
        self.ib.reqHistoricalData(self.reqId, contract, "1 hour", "2 D", str(self.barsize)+mintext, "MIDPOINT", 1, 1, True, [])

    #threading cont
    #Listen to socket in seperate thread
    def run_loop(self):
        self.ib.run()

    # Order setup
    def MarketOrder(self, action, quantity):
        #Create contract/Stock object to store stock info
        contract = Contract()
        contract.symbol = self.symbol.upper()
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity




    #Pass realtime bar data back to object
    def on_bar_update(self, reqId, bar, realtime):
        global orderId
        #Historical Data to catch up
        if (realtime == False):
            self.bars.append(bar)
        else:
            bartime = datetime.strptime(bar.date, "%Y%m%d %H:%M:%S").asttimezone(pytz.timezone("America/New_York"))
            minutes_diff = (bartime-self.initalbartime).total_seconds() / 60.0
            self.currentBar.date = bartime
            lastBar = self.bars[len(self.bars)-1]
            #On Bar Close
            if (minutes_diff > 0 and math.floor(minutes_diff) % self.barsize == 0):
                #Entry 
                closes = []
                for bar in self.bars:
                    closes.append(bar.close)
                
                #first EMA (9 period ema)
                self.close_array = pd.Series(np.asarray(closes))
                self.ema1 = ta.trend.EMAIndicator(self.close_array, self.ema1Period, True)
                print("EMA9 : " + str(self.ema1[len(self.ema1)-1]))
                #second EMA (21 period ema)
                self.close_array = pd.Series(np.asarray(closes))
                self.ema2 = ta.trend.EMAIndicator(self.close_array, self.ema2Period, True)
                print("EMA21 : " + str(self.ema2[len(self.ema2)-1]))

                #Criteria check
                if (self.ema1 > self.ema2):
                    #Order Buy
                    quantity = 1
                    mktOrder = self.MarketOrder("BUY", quantity)
                    self.ib.placeOrder(self.nextOrderId(), self.contract, mktOrder)
                    contract = Contract()
                    contract.symbol = self.symbol.upper()
                    contract.secType = "STK"
                    contract.exchange = "SMART"
                    contract.currency = "USD"
                    
                
                if (self.ema2 > self.ema1):
                    #Order Sell
                    quantity = 1
                    mktOrder = self.MarketOrder("SELL", quantity)
                    contract = Contract()
                    contract.symbol = self.symbol.upper()
                    contract.secType = "STK"
                    contract.exchange = "SMART"
                    contract.currency = "USD"
                
                self.ib.placeOrder(self.nextOrderId(), self.contract, mktOrder)
                orderId += 1

                #Bar closed append
                self.currentBar.close = bar.close
                if (self.currentBar.date != last)
                        


#Start bot
bot = Bot()


