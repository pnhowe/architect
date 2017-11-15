import string

# for now we are going to barrow parsimonious from contractor
from contractor.tscript.parsimonious import Grammar, ParseError, IncompleteParseError


# TODO: make sure a distrubution function is used

tcalc_grammar = """
script              = expression?
expression          = ws_s ( function / infix / boolean / not_ / variable / number_float / number_int ) ws_s

not_                = ~"[Nn]ot" expression

number_float        = ~"[-+]?[0-9]+\.[0-9]+"
number_int          = ~"[-+]?[0-9]+"
boolean             = ~"[Tt]rue" / ~"[Ff]alse"

function            = label "(" ( expression "," )* expression ")"
variable            = label !"("

infix               = "(" expression ( "^" / "*" / "/" / "%" / "+" / "-" / "&" / "|" / "and"/ "or" / "==" / "!=" / "<=" / ">=" / ">" / "<" ) expression ")"

label               = ~"[a-zA-Z][a-zA-Z0-9_]*"
ws_o                = ~"[ \t]"
ws_s                = ~"[ \t]*"
ws_p                = ~"[ \t]+"
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
                  # count
                  'scaled': '{0} * {1}',
                  'pd': '( {0} * {1} ) - ( {2} * {3} )',
                  # distrubution
                  'periodic': 'not bool( {0} % {1} )',
                  'above': '{0} > {1}',
                  # other
                }


class Function():
  def __init__( self, function, expected_variables ):
    super().__init__()
    self.function = function
    self.expected_variables = sorted( expected_variables )
    self.values = None

  def setValues( self, values ):
    if sorted( values.keys() ) != self.expected_variables:
      raise ValueError( 'Expected values "{0}" got "{1}"'.format( self.expected_variables, list( values.keys() ) ) )

    self.values = values

  def evaluate( self, index ):
    if self.values is None:
      raise ValueError( 'Values have not been set' )
    return bool( self.function( index, self.values ) )


class Parser():
  def __init__( self ):
    super().__init__()
    self.expected_variables = []
    self.grammar = Grammar( tcalc_grammar )

  def lint( self, script ):
    self.expected_variables = []

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
    self.expected_variables = []

    try:
      ast = self.grammar.parse( script )
    except IncompleteParseError as e:
      raise ParserError( e.column(), 'Incomplete Parse' )
    except ParseError as e:
      raise ParserError( e.column(), 'Error Parsing' )

    return Function( self._eval( ast ), list( set( self.expected_variables ) ) )

  def _eval( self, node ):
    if node.expr_name[ 0:3 ] == 'ws_':  # ignore wite space
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
      return lambda INDEX, v_map: False

    code = self._eval( node.children[0] )

    print( '** {0} **'.format( code ) )

    return lambda INDEX, v_map: eval( code )

  def expression( self, node ):
    return self._eval( node.children[1] )

  def number_float( self, node ):
    return '{0}'.format( float( node.text ) )

  def number_int( self, node ):
    return '{0}'.format( float( node.text ) )

  def boolean( self, node ):
    return '{0}'.format( True if node.text.lower() == 'true' else False )

  def variable( self, node ):
    name = node.children[0].text
    if name == 'INDEX':
      return 'INDEX'

    self.expected_variables.append( name )
    return 'v_map[ \'{0}\' ]'.format( name )

  def infix( self, node ):
    return '( {0} {1} {2} )'.format( self._eval( node.children[1] ), node.children[2].text, self._eval( node.children[3] ) )

  def not_( self, node ):
    return 'not {0}'.format( self._eval( node.children[1] ) )

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

    max_paramater = max( [ int( v[1] ) for v in string.Formatter().parse( func_body ) if v[1] is not None ] ) + 1
    if len( param_value_list ) != max_paramater:
      raise ValueError( 'Expected {0} paramaters, got {1}'.format( max_paramater, len( param_value_list ) ) )

    return function_map[ name ].format( *param_value_list )
