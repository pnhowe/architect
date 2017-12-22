import string

# for now we are going to barrow parsimonious from contractor
from contractor.tscript.parsimonious import Grammar, ParseError, IncompleteParseError


# TODO: make sure a distrubution function is used

tcalc_grammar = """
script              = line*
line                = definition? nl
definition          = ws ( blueprint / variable ) ws ":" expression
expression          = ws ( function / infix / boolean / not_ / external / ts_value / variable / number_float / number_int ) ws

not_                = ~"[Nn]ot" expression

number_float        = ~"[-+]?[0-9]+\.[0-9]+"
number_int          = ~"[-+]?[0-9]+"
boolean             = ~"[Tt]rue" / ~"[Ff]alse"

function            = label "(" ( expression "," )* expression ")"
external            = ( "*INDEX*" / "*TOTAL*" / "*COST*" / "*AVAILABILITY*" / "*RELIABILITY*" )
variable            = label !"("

infix               = "(" expression ( "^" / "*" / "/" / "%" / "+" / "-" / "&" / "|" / "and"/ "or" / "==" / "!=" / "<=" / ">=" / ">" / "<" ) expression ")"

label               = ~"[a-zA-Z][a-zA-Z0-9_\-]*"
ts_value            = ~"@[a-zA-Z][a-zA-Z0-9_\-]*"
blueprint           = ~"#[a-zA-Z0-9][a-zA-Z0-9_\-]*"
ws                  = ~"[ \t]*"
nl                  = ~"[\\r\\n]*"
"""


class ParserError( Exception ):
  def __init__( self, column, msg ):
    self.column = column
    self.msg = msg

  def __str__( self ):
    return 'ParseError, column: {0}, "{1}"'.format( self.column, self.msg )


def lint( script ):
  parser = Parser()
  return parser.lint( script )


def parse( script ):
  parser = Parser()
  return parser.parse( script )


# NOTE: Function paramaters must be numbered, so that the number of required
# functions is correctly detected
function_map = {
                  # distrubution
                  'periodic': 'not bool( {0} % {1} )',
                  # 'linear': 'bool( {0} == math.ceil( math.floor( ( {0} * ( {1} / _T_ ) ) + 0.00000000001 ) * ( _T_ / {1} ) ) )',
                  'linear': '{0} in linear_slots_{ID}',
                  'weighted': '{0} in weighted_slots_{ID}',

                  # subsetting
                  'above': '{0} > {1}',
                  'below': '{0} < {1}',
                  'above_inclusive': '{0} >= {1}',
                  'below_inclusive': '{0} <= {1}',

                  # other
                  'mult': '{0} * {1}'  # primary for testing, if there is another siimple function added later, use that instead of this
                }

function_init_map = {
                      'linear': """
  import math
  global linear_slots_{ID}
  if {1} > _T_ or {1} < 1:
    raise ValueError( 'Count should be more than 0 and less than the number of slots' )

  linear_slots_{ID} = [ math.ceil( i * ( _T_ / {1} ) ) for i in range( 0, int( {1} ) ) ]
""",

                      'weighted': """
  import math
  global weighted_slots_{ID}
  print( _T_, SLOTS_PER_BUCKET )

  avg_weight = float( sum( {2} ) ) / len( {2} )
  counter = 0
  weighted_slots_{ID} = []
  for i in range( 0, int( {1} ) ):
    bucket = int( counter / SLOTS_PER_BUCKET )
    try:
      interval = ( _T_ * ( avg_weight / {2}[ bucket ] ) ) / {1}
      interval = min( interval, SLOTS_PER_BUCKET )
    except ZeroDivisionError:
      interval = SLOTS_PER_BUCKET

    print( bucket, interval, counter )
    if interval < 1:
      raise ValueError( 'interval drops below 1' )

    counter += interval
    if counter > _T_:
      raise ValueError( 'Counter exceted total' )

    weighted_slots_{ID}.append( math.ceil( counter ) )
"""
}

"""
Functions:
  number per complex : number of  instances per complex = X % ( buckets per complex / count )
  weighted distrubution : = weighted value of curent complex / take the avertage of all the weights values -> factor that into even distrubution

  complex subset: prune down to bucekts that are in or out of list of complexes

for a/b testing: need above, below, every X


periodic: should produce the same result as [ INDEX for INDEX in range( 0, total_slots ) if not bool( INDEX % _PARAM_ ) ]  where *INDEX* is the first paramater
def periodic( i ):
  return not bool( i % PARAM )

( for non pre-computed version )
linear: should produce the same result as [ math.ceil( INDEX * ( total_slots / _PARAM_ ) ) for INDEX in range( 0, _PARAM_ ) ]  where *INDEX* is the first paramater
def linear( i ):
  return i == math.ceil( math.floor( ( i * ( COUNT / slot_count ) ) + 0.00000000001 ) * ( slot_count / COUNT ) )

NOTE: the magic number is to compensate for some small round down during the division
NOTE2: it is important that ( COUNT / slot_count ) be >= 1
"""

# TODO: how to do a dirivitave or integrated value....
# some kind of remember last value for a function
# mabey all the functions should exist in the same
# blob, and have a save for next time value per index
# if the functions get to involved we are going to need macros
# mabey for the first round we skip the PD controller and just scale
# with historsis


class Script():
  def __init__( self, code ):
    super().__init__()
    self.code = code
    self.slots_per_bucket = None
    self.ts_value_map = None

  def setBuckets( self, slots_per_bucket, bucket_cost, bucket_availability, bucket_reliability ):
    if not isinstance( slots_per_bucket, int ) or slots_per_bucket < 1 or slots_per_bucket > 10000:
      raise ValueError( 'slots_per_bucket must be int and from 1 to 10000' )
    if not isinstance( bucket_cost, list ) or not isinstance( bucket_availability, list ) or not isinstance( bucket_reliability, list ):
      raise ValueError( 'bucket_cost, bucket_availability, and bucket_reliability must be list' )
    if len( bucket_cost ) != len( bucket_availability ) != len( bucket_reliability ) or len( bucket_cost ) < 1 or len( bucket_cost ) > 1000:
      raise ValueError( 'bucket_cost, bucket_availability, and bucket_reliability must be the same size, and length from 1 to 1000' )

    self.slots_per_bucket = slots_per_bucket
    self.bucket_cost = bucket_cost
    self.bucket_availability = bucket_availability
    self.bucket_reliability = bucket_reliability
    self.total_slots = len( self.bucket_cost ) * self.slots_per_bucket

  def setTimeSeriesValues( self, ts_value_map ):
    if not isinstance( ts_value_map, dict ):
      raise ValueError( 'external_value_map must be a dict' )
    self.ts_value_map = ts_value_map

  def _evaluate( self, bucket, index ):
    try:
      value_map = self.code[ 'main' ]( index, self.total_slots, self.bucket_cost[ bucket ], self.bucket_availability[ bucket ], self.bucket_reliability[ bucket ], self.ts_value_map )
    except KeyError as e:
      raise ValueError( 'value "{0}" not defined'.format( e.args[0] ) )

    return dict( zip( value_map.keys(), [ i > 0 for i in value_map.values() ] ) )

  def evaluate( self ):
    if self.slots_per_bucket is None:
      raise ValueError( 'bucket info has not been set' )
    if self.ts_value_map is None:
      raise ValueError( 'timeseries values have not been set' )

    self.code[ '__builtins__' ][ 'SLOTS_PER_BUCKET' ] = self.slots_per_bucket

    if 'init' in self.code:
      self.code[ 'init' ]( self.total_slots, self.bucket_cost, self.bucket_availability, self.bucket_reliability, self.ts_value_map )

    result_name_list = self._evaluate( 0, 0 ).keys()
    result = dict( zip( result_name_list, [ [] for i in result_name_list ] ) )

    index = 0
    for bucket in range( 0, len( self.bucket_cost ) ):
      for offset in range( 0, self.slots_per_bucket ):
        tmp = self._evaluate( bucket, index )
        for key, value in tmp.items():
          if value:
            result[ key ].append( index )

        index += 1

    return result


class Parser():
  def __init__( self ):
    super().__init__()
    self.grammar = Grammar( tcalc_grammar )
    self.function_initers = []

  def lint( self, script ):
    self.function_initers = []
    try:
      ast = self.grammar.parse( script )
    except IncompleteParseError as e:
      return 'Incomplete Parsing at column: {0}'.format( e.column() )
    except ParseError as e:
      return 'Error Parsing at column: {0}'.format( e.column() )

    try:
      self._eval( ast )
    except Exception as e:
      return 'Exception Parsing "{0}"'.format( e )

    return None

  def parse( self, script ):
    self.function_initers = []
    try:
      ast = self.grammar.parse( script )
    except IncompleteParseError as e:
      raise ParserError( e.column(), 'Incomplete Parse' )
    except ParseError as e:
      raise ParserError( e.column(), 'Error Parsing' )

    init = ''

    body = self._eval( ast )

    if self.function_initers:
      init = 'def init( _T_, _C_, _A_, _R_, ts_map ):\n'
      for name, init_id, paramaters in self.function_initers:
        init += function_init_map[ name ].format( *paramaters, ID=init_id )

    script = init + """

def main( _I_, _T_, _C_, _A_, _R_, ts_map ):
  b_map = {}
  v_map = {}

""" + body + """

  return b_map
"""

    print( '*****************\n{0}\n*******************'.format( script ) )

    tmp = {}
    exec( compile( script, '<string>', 'exec' ), tmp )

    return Script( tmp )

  def _eval( self, node ):
    if node.expr_name in ( 'ws', 'nl' ):  # ignore wite space
      return ''

    if node.expr_name == '':
      return self._eval( node.children[0] )

    try:
      handler = getattr( self, node.expr_name )
    except AttributeError:
      raise Exception( 'Unable to find handler for "{0}"'.format( node.expr_name ) )

    return handler( node )

  def script( self, node ):
    if not node.children:
      return ''

    definition_list = [ self._eval( child ) for child in node.children ]
    return '\n'.join( definition_list )

  def line( self, node ):
    if len( node.children[0].children ) == 0:
      return ''

    return self._eval( node.children[0] )

  def definition( self, node ):  # ws variable ws ":" expression nl
    return '  {0} = {1}'.format( self._eval( node.children[1] ), self._eval( node.children[4] ) )

  def expression( self, node ):
    return self._eval( node.children[1] )

  def number_float( self, node ):
    return '{0}'.format( float( node.text ) )

  def number_int( self, node ):
    return '{0}'.format( float( node.text ) )

  def boolean( self, node ):
    return '{0}'.format( True if node.text.lower() == 'true' else False )

  def external( self, node ):
    name = node.text

    return '_{0}_'.format( name[1] )

  def ts_value( self, node ):
    name = node.text

    return 'ts_map[ \'{0}\' ]'.format( name[1] )

  def variable( self, node ):
    name = node.text

    return 'v_map[ \'{0}\' ]'.format( name )

  def blueprint( self, node ):
    name = node.text

    return 'b_map[ \'{0}\' ]'.format( name[ 1: ] )

  def infix( self, node ):
    return '( {0} {1} {2} )'.format( self._eval( node.children[1] ), node.children[2].text, self._eval( node.children[3] ) )

  def not_( self, node ):
    return 'not bool( {0} )'.format( self._eval( node.children[1] ) )

  def function( self, node ):
    param_value_list = []
    for child in node.children[2]:
      param_value_list.append( self._eval( child ) )
    param_value_list.append( self._eval( node.children[3] ) )
    name = node.children[0].text

    try:
      func_body = function_map[ name ]
    except KeyError:
      raise ValueError( 'Unknown function "{0}"'.format( name ) )

    print( '#### Parms "{0}"'.format( param_value_list ) )
    print( '**** Function "{0}"'.format( func_body ) )

    init_id = None
    if name in function_init_map:
      init_id = 'id{0}'.format( len( self.function_initers ) )
      self.function_initers.append( ( name, init_id, param_value_list ) )

    max_paramater = max( [ int( v[1] ) for v in string.Formatter().parse( func_body ) if v[1] is not None and v[1] not in ( 'ID', ) ] ) + 1
    if init_id is not None:
      max_paramater = max( [ max_paramater ] + [ int( v[1] ) for v in string.Formatter().parse( function_init_map[ name ] ) if v[1] is not None and v[1] not in ( 'ID', ) ] ) + 1

    if len( param_value_list ) != max_paramater:
      raise ValueError( 'Expected {0} paramaters, got {1}'.format( max_paramater, len( param_value_list ) ) )

    if init_id is not None:
      return function_map[ name ].format( *param_value_list, ID=init_id )
    else:
      return function_map[ name ].format( *param_value_list )
