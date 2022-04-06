import pandas as pd
from ib_insync import *

ib = IB()
ib.connect(clientId=1)

# init dataframe
df = pd.DataFrame(columns=['date', 'last'])
df.set_index('date', inplace=True)


def new_data(tickers):
    ''' process incoming data and check for trade entry '''
    for ticker in tickers:
        df.loc[ticker.time] = ticker.last

    five_mins_ago = df.index[-1] - pd.Timedelta(minutes=5)

    if df.index[0] < five_mins_ago:
        df = df[five_mins_ago:]

        price_min = df.last.min()
        price_max = df.last.max()

        if df.last[-1] > price_min * 1.05:
            submit_order('BUY')

        elif df[-1] < price_max * 0.95:
            submit_order('SELL')


def place_order(direction):
    ''' place order with IB - exit if order gets filled '''
    mastercard_order = MarketOrder(direction, 100)
    trade = ib.placeOrder(mastercard_contract, mastercard_order)
    ib.sleep(3)
    if trade.orderStatus.status == 'Filled':
        ib.disconnect()
        quit(0)


# Create contracts
mastercard_contract = Stock('MA', 'SMART', 'USD')
visa_contract = Stock('V', 'SMART', 'USD')

ib.qualifyContracts(mastercard_contract)
ib.qualifyContracts(visa_contract)

# Request market data for Visa
ib.reqMktData(visa_contract)

# Set callback function for tick data
ib.pendingTickersEvent += new_data

# Run infinitely
ib.run()
