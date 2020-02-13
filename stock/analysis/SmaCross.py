from datetime import datetime
import backtrader as bt

class SmaCross(bt.Strategy):
    params = dict(
        pfast=5,            # period for the fast moving average
        pslow=30            # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)      # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)      # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)       # crossover signal

    def next(self):
        if not self.position:       # not in the market
            if self.crossover > 0:      # if fast crosses slow to the upside
                close = self.data.close[0]      # close value
                size = int(self.broker.getcash() / close)       # available number

                self.buy(size=size)     # buy size
            elif self.crossover < 0:        # in the market & crossover to the downside
                self.close()            # sell

cerebro = bt.Cerebro()      # create a "cerebro" engine instance

# Samsung '005930.KS'
data = bt.feeds.YahooFinanceData(dataname='005930.KS',
                                 fromdate=datetime(2019,1,1),
                                 todate=datetime(2019,12,31))

cerebro.adddata(data)
cerebro.broker.setcash(1000000)
cerebro.broker.setcommission(commission=0.00015)        # fee
cerebro.addstrategy(SmaCross)           # strategy
cerebro.run()               # backtesting
cerebro.plot()


