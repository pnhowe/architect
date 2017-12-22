import time

from architect.lib.TimeSeries import getTS


def test_basicPutGet():
  ts = getTS()

  timestamp = time.time()

  ts_list = []
  ts_list.append( ( 'complex.test.cost' ( timestamp, 4 ) ) )
  ts.put( ts_list )
