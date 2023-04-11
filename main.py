from kline import kline_day
from indicator import Ind

df = kline_day('000008.XSHE')
print(df)

UPPER, MIDDLE, LOWER = Ind.BBANDS(df.close)
print(UPPER, MIDDLE, LOWER)
