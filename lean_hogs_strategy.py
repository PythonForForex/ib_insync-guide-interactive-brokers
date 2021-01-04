from ib_insync import *


ib = IB()
ib.connect()


def place_order(direction, qty, df, tp, sl):
    bracket_order = ib.bracketOrder(
        direction,
        qty,
        limitPrice=df.close.iloc[-1],
        takeProfitPrice=tp,
        stopLossPrice=sl,
    )

    for ord in bracket_order:
        ib.placeOrder(contract, ord)


def on_new_bar(bars: BarDataList, has_new_bar: bool):
    if has_new_bar:
        df = util.df(data)
        sma = df.close.tail(50).mean()
        std_dev = df.close.tail(50).std() * 3

        # Check if we are in a trade
        if contract not in [i.contract for i in ib.positions()]:
            # We are not in a trade - Look for a signal

            if df.close.iloc[-1] > sma + std_dev:
                # Trading more than 3 standard deviations above average - SELL
                place_order('SELL', 1, df, sma, sma + std_dev * 2)

            elif df.close.iloc[-1] < sma - std_dev:
                # Trading more than 3 standard deviations below average - BUY
                place_order('BUY', 1, df, sma,  sma - std_dev * 2)


# Create Contract
contract = ContFuture('HE', 'GLOBEX')
ib.qualifyContracts(contract)

# Request Streaming bars
data = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='2 D',
    barSizeSetting='15 mins',
    whatToShow='MIDPOINT',
    useRTH=True,
    keepUpToDate=True,
)

# Set callback function for streaming bars
data.updateEvent += on_new_bar

# Run infinitely 
ib.run()
