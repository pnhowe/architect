from django.db import models

from cinp.orm_django import DjangoCInP as CInP

cinp = CInP( 'TimeSeries', '0.1' )


class TimeSeries( models.Model ):
  pass
