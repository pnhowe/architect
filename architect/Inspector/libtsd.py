
import json
from http import client

from django.conf import settings

def getTSD():
  return OpenTSD( settings.OPENTSD_HOST, settings.OPENTSD_PORT )

class OpenTSD( object ):
  def __init__( self, opentsd_host, opentsd_port, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.opentsd_host = opentsd_host
    self.opentsd_port = opentsd_port

  def getValue( self, metric, start_offset ):
    url = 'http://{0}:{1}/api/query?start={2}m-ago&m=sum:{3}'.format( self.opentsd_host, self.opentsd_port, start_offset, metric )

    conn = client.HTTPConnection( self.opentsd_host, self.opentsd_port )
    conn.request( 'GET', url )
    resp = conn.getresponse()
    if resp.status != 200:
      raise Exception( 'Unknown status "{0}"'.format( resp.status ) )

    data = json.loads( resp.read() )
    resp.close()

    return data[ 0 ][ 'dps' ][ -1 ] # really should sort by the timestamp
