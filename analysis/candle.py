import pandas as pd
import pandas_datareader as pdr
from mpl_finance import candlestick2_ohlc
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


# 종목 타입에 따라 download url이 다름. 종목코드 뒤에 .KS .KQ등이 입력되어야해서 Download Link 구분 필요
stock_type = {
    'kospi': 'stockMkt',
    'kosdaq': 'kosdaqMkt'
}
# 회사명으로 주식 종목 코드를 획득할 수 있도록 하는 함수
def get_code(df, name):
    code = df.query("name=='{}'".format(name))['code'].to_string(index=False)
    # 위와같이 code명을 가져오면 앞에 공백이 붙어있는 상황이 발생하여 앞뒤로 sript() 하여 공백 제거
    code = code.strip()
    return code
# download url 조합
def get_download_stock(market_type=None):
    market_type = stock_type[market_type]
    download_link = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
    download_link = download_link + '?method=download'
    download_link = download_link + '&marketType=' + market_type
    df = pd.read_html(download_link, header=0)[0]
    return df;
# kospi 종목코드 목록 다운로드
def get_download_kospi():
    df = get_download_stock('kospi')
    df.종목코드 = df.종목코드.map('{:06d}.KS'.format)
    return df
# kosdaq 종목코드 목록 다운로드
def get_download_kosdaq():
    df = get_download_stock('kosdaq')
    df.종목코드 = df.종목코드.map('{:06d}.KQ'.format)
    return df

def EMA(close, timeperiod):  # Exponential Moving Average : 지수이동평균
    k = 2/(1+timeperiod) # k : smoothing constant
    close = close.dropna()
    ema = pd.Series(index=close.index)
    ema[timeperiod-1] = close.iloc[0:timeperiod].sum() / timeperiod
    for i in range(timeperiod,len(close)):
        ema[i] = close[i]*k + ema[i-1] * (1-k)
    return ema

def MACD(close, fastperiod=12, slowperiod=26, signalperiod=9):
    macd = EMA(close, fastperiod) - EMA(close, slowperiod)
    macd_signal = EMA(macd, signalperiod)
    macd_osc = macd - macd_signal
    df = pd.concat([macd, macd_signal, macd_osc],axis=1)
    df.columns = ['MACD','Signal','Oscillator']
    return df



# kospi, kosdaq 종목코드 각각 다운로드
kospi_df = get_download_kospi()
kosdaq_df = get_download_kosdaq()
# data frame merge
code_df = pd.concat([kospi_df, kosdaq_df])
# data frame정리
code_df = code_df[['회사명', '종목코드']]
# data frame title 변경 '회사명' = name, 종목코드 = 'code'
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
# 삼성전자의 종목코드 획득. data frame에는 이미 XXXXXX.KX 형태로 조합이 되어있음
code = get_code(code_df, '삼성전자')
# get_data_yahoo API를 통해서 yahho finance의 주식 종목 데이터를 가져온다.
df = pdr.get_data_yahoo(code)
print(df)



index = df.index.astype('str')
ma5 = df['Close'].rolling(window=5).mean()
ma20 = df['Close'].rolling(window=20).mean()
close_price = df['Close'].astype(float)
macd = MACD(close_price)


# 차트 레이아웃을 설정합니다.
fig = plt.figure(figsize=(12,10))
ax_main = plt.subplot2grid((5, 1), (0, 0), rowspan=3)
ax_sub = plt.subplot2grid((5, 1), (3, 0))
ax_sub2 = plt.subplot2grid((5, 1), (4, 0))

# 메인차트를 그립니다.
ax_main.set_title('Apple Inc. Q1~Q3 2018 Stock Price',fontsize=20)
ax_main.plot(index, ma5, label='MA5')
ax_main.plot(index, ma20, label='MA20')
candlestick2_ohlc(ax_main,df['Open'],df['High'],
                  df['Low'],df['Close'],width=0.6)

ax_main.legend(loc=5)

# 아래는 날짜 인덱싱을 위한 함수 입니다.
def mydate(x,pos):
    try:
        return index[int(x-0.5)]
    except IndexError:
        return ''

# ax_sub 에 MACD 지표를 출력합니다.
ax_sub.set_title('MACD',fontsize=15)
macd['MACD'].iloc[0] = 0
ax_sub.plot(index,macd['MACD'], label='MACD')
ax_sub.plot(index,macd['Signal'], label='MACD Signal')
ax_sub.legend(loc=2)

# ax_sub2 에 MACD 오실레이터를 bar 차트로 출력합니다.
ax_sub2.set_title('MACD Oscillator',fontsize=15)
oscillator = macd['Oscillator']
oscillator.iloc[0] = 1e-16
ax_sub2.bar(list(index),list(oscillator.where(oscillator > 0)), 0.7)
ax_sub2.bar(list(index),list(oscillator.where(oscillator < 0)), 0.7)

# x 축을 조정합니다.
ax_main.xaxis.set_major_locator(ticker.MaxNLocator(7))
ax_main.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
ax_sub.xaxis.set_major_locator(ticker.MaxNLocator(7))
ax_sub2.xaxis.set_major_locator(ticker.MaxNLocator(7))
fig.autofmt_xdate()

# 차트끼리 충돌을 방지합니다.
plt.tight_layout()
plt.show()