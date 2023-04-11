import pandas as pd
import talib as ta

class Ind:
    def __init__(self):
        pass
    
    ## 布林带
    def BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
        UPPER, MIDDLE, LOWER = ta.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype)
        return UPPER, MIDDLE, LOWER

    def DEMA(close, timeperiod=30):
        return ta.DEMA(close, timeperiod)

    def EMA(close, timeperiod=30):
        return ta.EMA(close, timeperiod)

    def HT_TRENDLINE(close):
        return ta.HT_TRENDLINE(close)

    def KAMA(close, timeperiod=30):
        return ta.KAMA(close, timeperiod)

    def MA(close, timeperiod=30, matype=0):
        return ta.MA(close, timeperiod, matype)

    def MA(close, timeperiod=30, matype=0):
        return ta.MA(close, timeperiod, matype)

    
