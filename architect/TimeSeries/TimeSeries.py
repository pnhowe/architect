

from django.conf import settings


def getTS():
  if settings.TSD_TYPE == 'Graphite':
    from architect.TimeSeries.Graphite import GraphiteTimeSeries

    return GraphiteTimeSeries( settings.GRAPHITE_HOST, settings.GRAPHITE_INJEST_PORT, settings.GRAPHITE_HTTP_PORT )

  elif settings.TSD_TYPE == 'OpenTSDB':
    from architect.TimeSeries.OpenTSDB import OpenTSDBTimeSeries

    return OpenTSDBTimeSeries( settings.OPENTSDB_HOST, settings.OPENTSDB_PORT )

  else:
    raise ValueError( 'Unknown TSD type '"{0}".format( settings.TSD_TYPE ) )


class TimeSeries():
  def __init__( self ):
    super().__init__()

  def put( self, data ):
    pass

  def get( self, metric, start_offset, end_offset ):
    pass

  def cleanUp( self, name ):
    pass

  def get_last( self, metric, max_age ):
    if not isinstance( metric, str ):
      raise ValueError( 'get_last only supports getting one metric' )  # TODO: add support for doing a list at some point

    data = self.get( metric, max_age, None )
    if data is None:
      return None

    try:
      while data[ -1 ] is None:
        data.pop()
    except IndexError:
      return None

    return data[ -1 ]
