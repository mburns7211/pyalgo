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

df = pd.DataFrame() # Instantiates DF for storage
mom = 3 # defines number of intervals for momentum strategy (3 ticks)
min_length = mom + 1 # specifies how many ticks to wait before starting

while True:
    data = socket.recv_string() # listen to zeromq for random ticks (used with tickserver)
    t = datetime.datetime.now() # timestamp of retrieval
    sym, value = data.split() # extract data
    df = pd.concat((df, pd.DataFrame({sym: float(value)}, index=[t]))) # add to timeseries df
    dr = df.resample('5s', label='right').last() # resample the data at 5 sec interval, taking last tick
    dr['returns'] = np.log(dr / dr.shift(1)) # calculates log returns over 5 second intervals
    if len(dr) > min_length: 
        min_length += 1 # increase min length of the resampled data
        dr['momentum'] = np.sign(dr['returns'].rolling(mom).mean()) # Calculates momentum
        print('\n' + '=' * 51)
        print('NEW SIGNAL | {}'.format(datetime.datetime.now()))
        print('=' * 51)
        print(dr.iloc[:-1].tail()) # prints 5 most recent rows
        if dr['momentum'].iloc[-2] == 1.0: # second most recent tick is used since most recent time interval is incomplete
            # in production would use latest data not -2
            print('\nLong market position.')
            # take some action (e.g. place buy order)
        elif dr['momentum'].iloc[-2] == -1.0:
            print('\nShort market position.')
            # take some action (e.g. place sell order)