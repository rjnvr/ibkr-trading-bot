# ibkr-trading-bot
A trading bot made using IBKR's TWS API and python

# Inputs
STOCK symbol to trade (can be entered in lowercase)
Barsize: Check IBKR's API accepted/Valid barsizes
input accepted in mins


# Bot Logic/Strategy

This bot utilizes the 9 ema and 21 ema crossover, Buying when the 9 ema crosses over the 21 ema on the close.
Selling when the 9 ema crosses under the 21 ema on the close.


