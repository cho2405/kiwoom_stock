from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import FinanceDataReader as fdr
fdr.__version__

class SmaCross1(Strategy):
    def init(self):
        Close = self.data.Close
        self.ma1 = self.I(SMA, Close, 10)
        self.ma2 = self.I(SMA, Close, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


data = fdr.DataReader('068270','20180104','20190630')
print(data.head())

bt = Backtest(data, SmaCross1, cash=10000, commission=.002)

bt.run()
bt.plot()