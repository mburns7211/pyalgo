#
# Python Script to Simulate a
# Financial Tick Data Server
#
# Python for Algorithmic Trading
# (c) Dr. Yves J. Hilpisch
# The Python Quants GmbH
#

# IMPLEMENTS A SIMULATION FOR RANDOM PRICE MOVEMENT

import zmq
import math
import time
import random

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://0.0.0.0:5555')


class InstrumentPrice(object):
    def __init__(self):
        self.symbol = 'SYMBOL'
        self.t = time.time() # time of initialization
        self.value = 100.
        self.sigma = 0.4
        self.r = 0.01

    def simulate_value(self):
        ''' Generates a new, random stock price. Using geometric brownian motion
        '''
        t = time.time() # time of simulated value
        dt = (t - self.t) / (252 * 8 * 60 * 60) # time difference between current time and init time in fractions of year (market days)
        dt *= 500 # To have large price movement, scales dt by arbitrary value
        self.t = t # updates so nex call uses current time as init time
        self.value *= math.exp((self.r - 0.5 * self.sigma ** 2) * dt +
                               self.sigma * math.sqrt(dt) * random.gauss(0, 1)) # calculates new price using euler scheme for brownian geometric motion
        return self.value


ip = InstrumentPrice()

while True:
    msg = '{} {:.2f}'.format(ip.symbol, ip.simulate_value()) # creates zeromq message
    print(msg)
    socket.send_string(msg) # publishes message to queue
    time.sleep(random.random() * 2) # randomly waits a period of time before starting again