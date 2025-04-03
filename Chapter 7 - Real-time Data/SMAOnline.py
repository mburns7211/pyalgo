#
# Python Script
# with Online Trading Algorithm
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#
import zmq
import datetime
import numpy as np
import pandas as pd

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://0.0.0.0:5555')
socket.setsockopt_string(zmq.SUBSCRIBE, 'SYMBOL')

df = pd.DataFrame()  # Instantiates DF for storage

# Define SMA parameters
sma1 = 5  # short-term SMA (5 intervals)
sma2 = 20  # long-term SMA (20 intervals)
min_length = sma2 + 1  # need at least sma2+1 data points to start

while True:
    data = socket.recv_string()  # listen to zeromq for random ticks (used with tickserver)
    t = datetime.datetime.now()  # timestamp of retrieval
    sym, value = data.split()  # extract data
    df = pd.concat((df, pd.DataFrame({sym: float(value)}, index=[t])))  # add to timeseries df
    dr = df.resample('5s', label='right').last()  # resample the data at 5 sec interval, taking last tick
    
    # Calculate SMAs
    if len(dr) >= sma1:
        dr['SMA1'] = dr[sym].rolling(window=sma1).mean()  # Short-term SMA
    
    if len(dr) >= sma2:
        dr['SMA2'] = dr[sym].rolling(window=sma2).mean()  # Long-term SMA
        
    # Calculate position based on SMA crossover
    if len(dr) >= sma2:
        # Initialize position column if it doesn't exist
        if 'position' not in dr.columns:
            dr['position'] = np.nan
            
        # Update position: 1 when SMA1 > SMA2 (bullish), -1 when SMA1 < SMA2 (bearish)
        dr['position'] = np.where(dr['SMA1'] < dr['SMA2'], 1, -1)
    
    if len(dr) > min_length:
        min_length += 1  # increase min length of the resampled data
        
        print('\n' + '=' * 51)
        print('NEW SIGNAL | {}'.format(datetime.datetime.now()))
        print('=' * 51)
        print(dr.iloc[:-1].tail())  # prints 5 most recent rows
        
        if 'position' in dr.columns and not pd.isna(dr['position'].iloc[-2]):
            if dr['position'].iloc[-2] == 1.0:  # second most recent tick is used since most recent time interval is incomplete
                # in production would use latest data not -2
                print('\nLong market position.')
                # take some action (e.g. place buy order)
            elif dr['position'].iloc[-2] == -1.0:
                print('\nShort market position.')
                # take some action (e.g. place sell order)