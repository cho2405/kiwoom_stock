import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'nanummyeongjo'
plt.rcParams['figure.figsize'] = (12, 4)
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['axes.grid'] = True

import FinanceDataReader as fdr
print(fdr.__version__)
df_krx = fdr.StockListing('KRX')
df = fdr.DataReader('011070', '2020')
print(df)



df.to_csv('./analysis/data/011070_2020.csv', mode='w')



ma_ls = [5, 10, 15, 20]
for i in range(len(ma_ls)):
    a = df['Close'].rolling(window=ma_ls[i]).mean()
    df['MA' + str(ma_ls[i])] = a

print(df)

plt.plot(df.index, df.iloc[:, [3,6,7,8,9]], label="종가")
plt.grid()
plt.title("Moving Area")
#plt.show()

df.dropna(inplace=True, axis=0)
date_index = abs(df['MA10']-df['MA20']).sort_values().head(10).index
print(date_index)

import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='black', width=4), name="Close"))
fig.add_trace(go.Scatter(x=df.index, y=df['MA10'], mode='lines', name="Close"))
fig.update_layout(title='Close and Moving Average@5, 10, 15, 20',
                  xaxis_title='days', yaxis_title='Stock Value')
fig.show()

