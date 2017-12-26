import pickle
import struct
import socket
import http

from architect.TimeSeries.TimeSeries import TimeSeries


class GraphiteTimeSeries( TimeSeries ):
  def __init__( self, host, injest_port, http_port ):
    super().__init__()
    self.host = host
    self.injest_port = injest_port
    self.http_port = http_port

  def put( self, data ):
    payload = pickle.dumps( data, protocol=2 )
    soc = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    soc.connect( ( self.host, self.injest_port ) )
    soc.send( struct.pack( '!L', len( payload ) ) + payload )
    soc.close()

  def _baseHTTPUrl( self, metric, start_offset, end_offset ):
    start = '-{0}s'.format( start_offset )
    if end_offset is None:
      end = ''
    else:
      end = '&until=-{0}s'.format( end_offset )

    if isinstance( metric, list ):
      targets = ',\'30s\')&target=movingAverage('.join( metric )
    else:
      targets = metric

    return '/render?from={0}{1}&target=movingAverage({2},\'30s\')'.format( start, end, targets )

  def get( self, metric, start_offset, end_offset ):
    url = self._baseHTTPUrl( metric, start_offset, end_offset ) + '&format=pickle'
    conn = http.client.HTTPConnection( self.host, self.http_port )
    conn.request( 'GET', url )
    resp = conn.getresponse()
    if resp.status != 200:
      raise Exception( 'Unknown status "{0}"'.format( resp.status ) )

    data = pickle.loads( resp.read() )
    if len( data ) == 0:
      return None

    if len( data ) == 1:
      return data[0][ 'values' ]

    result = {}
    for item in data:
      result[ item['name'] ] = item[ 'values' ]

    return result

  def cleanUp( self, name ):
    pass

  # old stuff

  def putCheckpoint( self, name, timestamp, value, normalized, target, max_, min_, deadband_high, deadband_low ):
    data = []
    data.append( ( '{0}.cur'.format( name ), ( timestamp, value ) ) )
    data.append( ( '{0}.norm'.format( name ), ( timestamp, normalized ) ) )
    data.append( ( '{0}.tar'.format( name ), ( timestamp, target ) ) )
    data.append( ( '{0}.max'.format( name ), ( timestamp, max_ ) ) )
    data.append( ( '{0}.min'.format( name ), ( timestamp, min_ ) ) )
    data.append( ( '{0}.db_high'.format( name ), ( timestamp, deadband_high ) ) )
    data.append( ( '{0}.db_low'.format( name ), ( timestamp, deadband_low ) ) )
    self._put( data )

  def putProvisionedState( self, name, timestamp, active, provisioning, deprovisioining ):
    data = []
    data.append( ( '{0}.active'.format( name ), ( timestamp, active ) ) )
    data.append( ( '{0}.prov'.format( name ), ( timestamp, provisioning ) ) )
    data.append( ( '{0}.deprov'.format( name ), ( timestamp, deprovisioining ) ) )
    self._put( data )

  def getGraph( self, name, start_offset, end_offset, height, width ):
    start = '-{0}min'.format( start_offset )
    if end_offset == 0:
      end = 'now'
    else:
      end = '-{0}min'.format( end_offset )
    return 'http://{0}:{1}/render?from={2}&until={3}&width={4}&height={5}&target=secondYAxis({6}.{{cur,norm}})&target={6}.{{calc,tar}}&target=color({6}.{{db_low,db_high}},"ffaaaa")&target=color({6}.{{max,min}},"aaaaff")'.format( self.host, self.http_port, start, end, width, height, name )

  def getCurState( self, name, timespan ):  # timespan in seconds
    url = '/render?target=keepLastValue({0}.cur)&target=keepLastValue({0}.norm)&target=keepLastValue({0}.calc)&target=keepLastValue({0}.db_high)&target=keepLastValue({0}.db_low)&from=-{1}sec&format=pickle'.format( name, ( timespan * 8 ) )
    conn = http.client.HTTPConnection( self.host, self.http_port )
    conn.request( 'GET', url )
    resp = conn.getresponse()
    if resp.status != 200:
      raise Exception( 'Unknown status "{0}"'.format( resp.status ) )

    result = { 'cur': None }
    timestamp = None
    data = pickle.loads( resp.read() )
    for item in data:
      if item[ 'name' ].endswith( '.cur)' ):
        result[ 'cur' ] = filter( lambda x: x is not None, item[ 'values' ] )[ -3: ]
        timestamp = item[ 'end' ] - timespan
      elif item[ 'name' ].endswith( '.tar)' ):
        result[ 'tar' ] = item[ 'values' ][ -1 ]
      elif item[ 'name' ].endswith( '.norm)' ):
        result[ 'norm' ] = item[ 'values' ][ -1 ]
      elif item[ 'name' ].endswith( '.db_high)' ):
        result[ 'db_high' ] = item[ 'values' ][ -1 ]
      elif item[ 'name' ].endswith( '.db_low)' ):
        result[ 'db_low' ] = item[ 'values' ][ -1 ]

    if timestamp is None or not result[ 'cur' ]:  # could be None or []
      return ( None, timestamp )

    while len( result[ 'cur' ] ) < 3:
      result[ 'cur' ] = [ result[ 'cur' ][0] ] + result[ 'cur' ]  # prepend, this in reverse chron order

    return ( result, timestamp )
