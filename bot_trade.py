import ccxt
import pandas as pd
from finta import TA  # Import finta library for technical analysis
from datetime import datetime, timedelta
import numpy as np

# Initialize the Indodax exchange
exchange = ccxt.indodax()

# Set parameters
symbol = 'BTC/IDR'  # Bitcoin to Indonesian Rupiah (or another symbol pair)
timeframe = '1h'  # 1-hour candles

# Get the current date and subtract 1 week (7 days ago) to get the start point
now = exchange.milliseconds()  # Get current time in milliseconds
one_week_ago = now - (31 * 24 * 60 * 60 * 1000)  # 7 days ago in milliseconds

# Initialize an empty list to hold all the data
all_ohlcv_data = []

# Fetch data in a loop to handle the 1000-row limit
while one_week_ago < now:
    ohlcv_data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=one_week_ago, limit=1000)
    
    # Append fetched data to the list
    all_ohlcv_data += ohlcv_data
    
    # If the data is less than 1000 rows, we've reached the end, so break the loop
    if len(ohlcv_data) < 1000:
        break
    
    # Update the 'since' time to the last timestamp in the fetched data (to continue fetching the next batch)
    one_week_ago = ohlcv_data[-1][0] + 1  # Adding 1 to avoid fetching the same data twice

# Convert data into a DataFrame
columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
df = pd.DataFrame(all_ohlcv_data, columns=columns)

# Convert timestamp to a readable date format
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Calculate Technical Indicators using Finta

# 1. RSI (Relative Strength Index)
df['rsi'] = TA.RSI(df)

# 2. EMA (Exponential Moving Average)
df['ema'] = TA.EMA(df, period=14)

# 3. SMA (Simple Moving Average)
df['sma'] = TA.SMA(df, period=20)

# 4. MACD (Moving Average Convergence Divergence)
macd = TA.MACD(df)
df['macd'] = macd['MACD']
df['macd_signal'] = macd['SIGNAL']

# 5. Bollinger Bands
bollinger_bands = TA.BBANDS(df)
df['bb_upper'] = bollinger_bands['BB_UPPER']
df['bb_middle'] = bollinger_bands['BB_MIDDLE']
df['bb_lower'] = bollinger_bands['BB_LOWER']

# 6. VWAP (Volume Weighted Average Price)
df['vwap'] = TA.VWAP(df)

# 7. Parabolic SAR (manually implemented)
def parabolic_sar(df, af=0.02, max_af=0.2):
    high = df['high']
    low = df['low']
    close = df['close']
    psar = np.zeros(len(close))
    bull = True
    af = af
    ep = low[0]  # Initial extreme point
    sar = high[0]  # Initial SAR

    for i in range(1, len(close)):
        prior_sar = sar
        sar = prior_sar + af * (ep - prior_sar)

        if bull:
            if low[i] < sar:
                bull = False
                sar = ep
                ep = low[i]
                af = 0.02
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + 0.02, max_af)
        else:
            if high[i] > sar:
                bull = True
                sar = ep
                ep = high[i]
                af = 0.02
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + 0.02, max_af)

        psar[i] = sar

    return psar

df['psar'] = parabolic_sar(df)

# 8. Stochastic Oscillator (manual calculation)
def stochastic_oscillator(df, period=14):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
    stoch_d = stoch_k.rolling(window=3).mean()  # Stochastic D is a 3-period SMA of Stochastic K
    return stoch_k, stoch_d

df['stoch_k'], df['stoch_d'] = stochastic_oscillator(df)

# 9. Fibonacci Retracement (based on the entire data period)
high_price = df['high'].max()
low_price = df['low'].min()
fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
for level in fib_levels:
    df[f'fib_{level}'] = low_price + (high_price - low_price) * level

# Display the first few rows of the DataFrame with indicators
# print(df[['timestamp', 'close', 'rsi', 'ema', 'sma', 'macd', 'macd_signal', 'bb_upper', 'bb_middle', 'bb_lower', 'vwap', 'psar', 'stoch_k', 'stoch_d']].head())
# print(df)
# Optional: Save the data with indicators to a CSV file
# df.to_csv('btc_idr_historical_data_with_finta_and_custom_indicators_1h_1week.csv', index=False)
return df