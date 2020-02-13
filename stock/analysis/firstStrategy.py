import backtrader as bt
from datetime import datetime

class firstStrategy(bt.Strategy):
    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 30:
                self.buy(size=100)
        else:
            if self.rsi > 70:
                self.sell(size=100)

startcash = 10000
cerebro = bt.Cerebro()

cerebro.addstrategy(firstStrategy)
data = bt.feeds.YahooFinanceData(dataname='005930.KS',
                                 fromdate=datetime(2019,1,1),
                                 todate=datetime(2019,12,31))
cerebro.adddata(data)
cerebro.broker.setcash(startcash)
cerebro.run()

portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

cerebro.plot(style='candlestick')
