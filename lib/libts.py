import pickle
import struct
import socket
import http

from django.conf import settings

def getTS():
  return GraphiteTimeSeries( settings.GRAPHITE_HOST, settings.GRAPHITE_INGEST_PORT, settings.GRAPHITE_HTTP_PORT )

class TimeSeries( object ):
  def __init__( self, *args, **kwargs ):
    pass

class GraphiteTimeSeries( TimeSeries ):
  def __init__( self, graphite_host, graphite_injest_port, graphite_http_port, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.graphite_host = graphite_host
    self.graphite_injest_port = graphite_injest_port
    self.graphite_http_port = graphite_http_port

  def _put( self, data ):
    payload = pickle.dumps( data, protocol=2 )
    soc = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    soc.connect( ( self.graphite_host, self.graphite_injest_port ) )
    soc.send( struct.pack( '!L', len( payload ) ) + payload )
    soc.close()

  def cleanUp( self, name ):
    pass

  def putSample( self, name, timestamp, value ):
    data = []
    data.append( ( '{0}.cur'.format( name ), ( timestamp, value ) ) )
    self._put( data )

  def putControl( self, name, timestamp, predicted, deadband_high, deadband_low ):
    data = []
    data.append( ( '{0}.pred'.format( name ), ( timestamp, predicted ) ) )
    data.append( ( '{0}.db_high'.format( name ), ( timestamp, deadband_high ) ) )
    data.append( ( '{0}.db_low'.format( name ), ( timestamp, deadband_low ) ) )
    self._put( data )

  def putCurent( self, name, timestamp, active, provisioning, deprovisioining ):
    data = []
    data.append( ( '{0}.active'.format( name ), ( timestamp, active ) ) )
    data.append( ( '{0}.prov'.format( name ), ( timestamp, provisioning ) ) )
    data.append( ( '{0}.deprov'.format( name ), ( timestamp, deprovisioining ) ) )
    self._put( data )

  def getGraph( self, name, start_offset, end_offset, height, width ):
    start = '-%smin' % start_offset
    if end_offset == 0:
      end = 'now'
    else:
      end = '-%smin' % end_offset
    return 'http://{0}:{1}/render?from={2}&until={3}&width={4}&height={5}&target=secondYAxis({6}.cur)&target=secondYAxis({6}.pred)&target={6}.calc&target=areaBetween({6}.{db_low,db_high})&areaMode=stacked&areaAlpha=0.8'.format( self.graphite_host, self.graphite_http_port, start, end, width, height, name )

  def getCurState( self, name, timespan ): # timespan in seconds
    url = '/render?target=keepLastValue({0}.cur)&target=keepLastValue({0}.pred)&target=keepLastValue({0}.calc)&target=keepLastValue({0}.db_high)&target=keepLastValue({0}.db_low)&from=-{1}sec&format=pickle'.format( name, ( timespan * 8 ) )
    conn = http.client.HTTPConnection( self.graphite_host, self.graphite_http_port )
    conn.request( 'GET', url )
    resp = conn.getresponse()
    if resp.status != 200:
      raise Exception( 'Unknown status "%s"' % resp.status )

    result = { 'cur': None }
    timestamp = None
    data = pickle.loads( resp.read() )
    for item in data:
      if item[ 'name' ].endswith( '.cur)' ):
        result[ 'cur' ] = filter( lambda x: x is not None, item[ 'values' ] )[ -3: ]
        timestamp = item[ 'end' ] - timespan
      elif item[ 'name' ].endswith( '.pred)' ):
        result[ 'pred' ] = item[ 'values' ][ -1 ]
      elif item[ 'name' ].endswith( '.db_high)' ):
        result[ 'db_high' ] = item[ 'values' ][ -1 ]
      elif item[ 'name' ].endswith( '.db_low)' ):
        result[ 'db_low' ] = item[ 'values' ][ -1 ]

    if timestamp is None or not result[ 'cur' ]: # could be None or []
      return ( None, timestamp )

    while len( result[ 'cur' ] ) < 3:
      result[ 'cur' ] = [ result[ 'cur' ][0] ] + result[ 'cur' ] # prepend, this in reverse chron order

    return ( result, timestamp )
