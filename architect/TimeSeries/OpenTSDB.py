
import json
from http import client

from architect.TimeSeries.TimeSeries import TimeSeries


class OpenTSDTimeSeries( TimeSeries ):
  def __init__( self, host, port ):
    super().__init__()
    self.host = host
    self.port = port

  def getValue( self, metric, start_offset ):
    url = 'http://{0}:{1}/api/query?start={2}m-ago&m=sum:{3}'.format( self.opentsd_host, self.opentsd_port, start_offset, metric )

    conn = client.HTTPConnection( self.host, self.port )
    conn.request( 'GET', url )
    resp = conn.getresponse()
    if resp.status != 200:
      raise Exception( 'Unknown status "{0}"'.format( resp.status ) )

    data = json.loads( resp.read() )
    resp.close()

    return data[ 0 ][ 'dps' ][ -1 ]  # really should sort by the timestamp
