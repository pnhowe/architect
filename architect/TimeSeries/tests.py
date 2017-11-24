from django.test import TestCase

import time

from architect.lib.libts import GraphiteTimeSeries

def test_basicPutGet():
  ts = time.time()
  gts = GraphiteTimeSeries( 'localhost', 2004, 80 )
  gts.putSample( 'test', ts, 5 )
  gts.putSample( 'test', ts + 1, 6 )
  gts.putSample( 'test', ts + 2, 7 )
  gts.getEntry( 'test', ts )
