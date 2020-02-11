import pandas as pd
import numpy as np
import plotly.graph_objects as go

data = pd.read_csv('./data/011070_2020.csv')

data.columns = ['Date','Open', 'High', 'Low','Close', 'Volumn', 'Change']

def cal_ema_macd(data, n_fast=12, n_slow=26, n_signal=9):
    data['EMAFast'] = data['Close'].ewm(span=n_fast).mean()
    data['EMASlow'] = data['Close'].ewm(span=n_slow).mean()
    data['MACD'] = data['EMAFast']- data['EMASlow']
    data['MACDSignal'] = data['MACD'].ewm(span=n_signal).mean()
    data['MACDDiff'] = data['MACD'] - data['MACDSignal']

    return data

data = cal_ema_macd(data)
import plotly.graph_objects as go
fig = go.Figure()
#fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=data.index, y=data['MACD'], mode='lines', name='MACD'))
fig.add_trace(go.Scatter(x=data.index, y=data['MACDSignal'], mode='lines', name='MACD Signal'))
fig.add_trace(go.Bar(x=data.index, y=data['MACDDiff'], name='MACD Diff', width=2.5, marker_color='Black'))
fig.add_trace(go.Scatter(x=data.index, y=np.zeros(len(data.index)), name='0', line = dict(color='gray', width=2, dash='dot')))

fig.update_layout(title='MACD', xaxis_title='days', yaxis_title='MACD')
fig.show()