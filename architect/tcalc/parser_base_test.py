import pytest

from architect.tcalc.parser import parse, lint, ParserError, function_map, function_init_map


def test_parse():
  assert lint( '' ) is None
  parse( '' )  # TODO: figoure out a way to make sure it compiled the right thing

  assert lint( 'a:asd' ) is None
  parse( 'a:asd' )
  assert lint( 'a: asd' ) is None
  parse( 'a: asd' )
  assert lint( 'a :asd' ) is None
  parse( 'a :asd' )
  assert lint( 'a : asd' ) is None
  parse( 'a : asd' )

  assert lint( 'a: 42' ) is None
  parse( 'a: 42' )

  assert lint( '*' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
    parse( '*' )

  parse( 'a: ( asd + zxc )' )

  parse( 'a: ( asd + asd )' )

  parse( 'a: not ( qwerty % 10 )' )

  parse( 'a: 5' )
  parse( '\na: 5' )
  parse( 'a: 5\n' )
  parse( '\n\na: 5\n\n' )

  assert lint( 'a: asdf()' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
    parse( 'a: asdf()' )

  assert lint( 'a: above()' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
    parse( 'a: above()' )

  assert lint( 'a: above( a, b )' ) is None
  parse( 'a: above( a, b )' )

  parse( '#sdf: 5' )
  with pytest.raises( ParserError ):
    parse( '@adf: 5' )

  parse( 'a: *INDEX*' )
  parse( 'a: *TOTAL*' )
  parse( 'a: *COST*' )
  parse( 'a: *AVAILABILITY*' )
  parse( 'a: *RELIABILITY*' )

  parse( 'a: @b' )
  parse( '#a: @b' )
  parse( 'a123: @b332' )
  parse( '#a123: @b332' )
  parse( 'asdf: @bwer' )
  parse( '#asdf: @bwer' )

  parse( 'a: ( *INDEX* + asd )' )
  parse( 'a: ( *AVAILABILITY* + asd )' )

  parse( 'a: not ( *INDEX* % 10 )' )
  parse( 'a: not ( *AVAILABILITY* % 10 )' )


def test_bucket_setup():
  f = parse( '' )
  with pytest.raises( ValueError ):
    f.evaluate()

  f.setBuckets( 1, [ 0 ], [ 1 ], [ 2 ] )
  assert f.total_slots == 1
  assert f.bucket_cost == [ 0 ]
  assert f.bucket_availability == [ 1 ]
  assert f.bucket_reliability == [ 2 ]

  with pytest.raises( ValueError ):
    f.setBuckets( 'a', [ 0 ], [ 1 ], [ 2 ] )

  with pytest.raises( ValueError ):
    f.setBuckets( 1, [], [ 1 ], [ 2 ] )

  with pytest.raises( ValueError ):
    f.setBuckets( 1, 'a', [ 1 ], [ 2 ] )

  f.setBuckets( 10, [ 0 ], [ 1 ], [ 2 ] )
  assert f.total_slots == 10

  f.setBuckets( 10, [ 0, 1, 2 ], [ 1, 1, 1 ], [ 2, 2, 2 ] )
  assert f.total_slots == 30


def test_basic_evaluation():
  f = parse( '#a: 5' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 5 }
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setBuckets( 1, [ 0 ], [ 0 ], [ 0 ] )
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0 ] }

  f = parse( 'b: 5\n#a: b' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 5 }
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setBuckets( 1, [ 0 ], [ 0 ], [ 0 ] )
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0 ] }

  f = parse( '#a: *INDEX*' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 1 }
  assert f.code[ 'main' ]( 5, 1, 0, 0, 0, {} ) == { 'a': 5 }
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setBuckets( 5, [ 0 ], [ 0 ], [ 0 ] )
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4 ] }

  f = parse( '#a: *INDEX*\n#b: *TOTAL*\n#c: *COST*' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 1, 'b': 1, 'c': 0 }
  assert f.code[ 'main' ]( 9, 7, 5, 0, 0, {} ) == { 'a': 9, 'b': 7, 'c': 5 }
  f.setBuckets( 5, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4 ], 'b': [ 0, 1, 2, 3, 4 ], 'c': [ 0, 1, 2, 3, 4 ] }

  f.setBuckets( 1, [ -1, -2, 1, 10, 0 ], [ 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0 ] )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4 ], 'b': [ 0, 1, 2, 3, 4 ], 'c': [ 2, 3, 4 ] }

  f = parse( 'x: 40\ny: 2\n#a: ( x + y )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 42 }

  f = parse( 'x: 10\n#a: ( x + *INDEX* )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 11 }
  assert f.code[ 'main' ]( 5, 1, 0, 0, 0, {} ) == { 'a': 15 }

  f = parse( '#a: b' )  # test non existant vars
  f.setBuckets( 1, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  with pytest.raises( KeyError ):
    f.code[ 'main' ]( 1, 1, 0, 0, 0, {} )
  with pytest.raises( ValueError ):
    f.evaluate()


def test_buckt_info_merge():
  f = parse( '#a: ( ( ( ( 2 * *INDEX* ) + ( 3 * *TOTAL* ) ) + ( ( 5 * *COST* ) + ( 7 * *AVAILABILITY* ) ) ) + ( 11 * *RELIABILITY* ) )\n#b: ( #a >= 0 )' )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': 0, 'b': True }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 2, 'b': True }
  assert f.code[ 'main' ]( 0, 1, 0, 0, 0, {} ) == { 'a': 3, 'b': True }
  assert f.code[ 'main' ]( 0, 0, 1, 0, 0, {} ) == { 'a': 5, 'b': True }
  assert f.code[ 'main' ]( 0, 0, 0, 1, 0, {} ) == { 'a': 7, 'b': True }
  assert f.code[ 'main' ]( 0, 0, 0, 0, 1, {} ) == { 'a': 11, 'b': True }

  f.setBuckets( 3, [ 0, 0, 0 ], [ 0, 0, 0 ], [ 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8 ], 'b': [ 0, 1, 2, 3, 4, 5, 6, 7, 8 ] }

  f.setBuckets( 3, [ -10, 0, -40 ], [ 0, 0, 0 ], [ 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 3, 4, 5 ], 'b': [ 3, 4, 5 ] }


def test_ts_value_merge():
  f = parse( '#a: @b' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, { 'b': 21 } ) == { 'a': 21 }
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setBuckets( 1, [ 0 ], [ 0 ], [ 0 ] )
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setTimeSeriesValues( { 'b': 1234 } )
  assert f.evaluate() == { 'a': [ 0 ] }

  f = parse( 'b: 10\n#a: ( @b + b )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, { 'b': 21 } ) == { 'a': 31 }
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setBuckets( 1, [ 0 ], [ 0 ], [ 0 ] )
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setTimeSeriesValues( { 'b': 1234 } )
  assert f.evaluate() == { 'a': [ 0 ] }


def test_basic_function():
  function_map[ 'testfunc' ] = '{0} + {1}'

  f = parse( '#a: testfunc( 3, 5 )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 8 }
  f.setBuckets( 2, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1 ] }

  f = parse( 'x: 10\ny: 2\n#a: testfunc( x, y )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 12 }
  f.setBuckets( 2, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1 ] }

  f = parse( '#a: testfunc( *INDEX*, 1.2 )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 2.2 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 11.2 }
  f.setBuckets( 2, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1 ] }

  f = parse( '#a: testfunc( *COST*, 1.2 )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 1.2 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 1.2 }
  assert f.code[ 'main' ]( 10, 1, 2, 0, 0, {} ) == { 'a': 3.2 }
  f.setBuckets( 2, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1 ] }


def test_init_function():
  function_map[ 'testfunc' ] = 'testfunc_{ID}'
  function_init_map[ 'testfunc' ] = """  global testfunc_{ID}
  val1 = {0}
  val2 = {1}
  if isinstance( val1, list ) and isinstance( val2, list ):
    testfunc_{ID} = sum( [ val1[ i ] + val2[ i ] for i in range( 0, len( val1 ) ) ] )
  elif isinstance( val1, list ):
    testfunc_{ID} = sum( [ i + val2 for i in val1 ] )
  elif isinstance( val2, list ):
    testfunc_{ID} = sum( [ val1 + i for i in val2 ] )
  else:
    testfunc_{ID} = val1 + val2
"""

  f = parse( '#a: testfunc( 3, 5 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 8 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 8 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  with pytest.raises( ValueError ):
    parse( '#a: testfunc( *INDEX*, 5 )' )

  f = parse( '#a: testfunc( *TOTAL*, 5 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 15 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 15 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( ( *TOTAL* * 3 ), 5 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 35 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 35 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( 6, ( *TOTAL* * 2 ) )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 26 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 26 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( *COST*, 5 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 5 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 5 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( ( *COST* * 3 ), 5 )' )
  f.code[ 'init' ]( 10, [ 1 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 8 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 8 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( 6, ( *COST* * 2 ) )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 6 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 6 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( *COST*, 5 )' )
  f.code[ 'init' ]( 10, [ 2, 5 ], [ 0, 0 ], [ 0, 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 17 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 17 }
  f.setBuckets( 10, [ 2, 5 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] }

  f = parse( '#a: testfunc( ( *COST* * 3 ), 5 )' )
  f.code[ 'init' ]( 10, [ 2, 5 ], [ 0, 0 ], [ 0, 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 31 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 31 }
  f.setBuckets( 10, [ 2, 5 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] }

  f = parse( '#a: testfunc( ( *AVAILABILITY* / 2 ), ( *COST* * 2 ) )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 0 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 0 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( ( *AVAILABILITY* / 2 ), ( *COST* * 2 ) )' )
  f.code[ 'init' ]( 10, [ 1, 2 ], [ 4, 8 ], [ 0, 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 12}
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 12 }
  f.setBuckets( 10, [ 1, 2 ], [ 4, 8 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] }

  f = parse( '#a: testfunc( ( *AVAILABILITY* / 2 ), ( *COST* * 2 ) )' )
  f.code[ 'init' ]( 10, [ 1, 0 ], [ 0, 0 ], [ 0, 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 2 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 2 }
  f.setBuckets( 10, [ 1, 0 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] }

  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( x, 7 )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( 7, x )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( *INDEX*, 7 )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( 7, *INDEX* )' )

  function_map[ 'testfunc' ] = 'testfunc_{ID} + {2}'

  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( x, 7, 1 )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( 1, x, 4 )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( *INDEX*, 1, 7 )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( 1, *INDEX*, 4 )' )

  f = parse( 'x: 10\n#a: testfunc( 1, 7, x )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 18 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 18 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( 1, 7, *INDEX* )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 9 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 18 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  function_map[ 'testfunc' ] = 'testfunc_{ID} * {0}'
  function_init_map[ 'testfunc' ] = """  global testfunc_{ID}
  val1 = {1}
  val2 = {2}
  if isinstance( val1, list ) and isinstance( val2, list ):
    testfunc_{ID} = sum( [ val1[ i ] + val2[ i ] for i in range( 0, len( val1 ) ) ] )
  elif isinstance( val1, list ):
    testfunc_{ID} = sum( [ i + val2 for i in val1 ] )
  elif isinstance( val2, list ):
    testfunc_{ID} = sum( [ val1 + i for i in val2 ] )
  else:
    testfunc_{ID} = val1 + val2
"""
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( 1, 7, x )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( 1, x, 4 )' )
  with pytest.raises( ValueError ):
    parse( '#a: testfunc( 1, 7, *INDEX* )' )
  with pytest.raises( ValueError ):
    parse( '#a: testfunc( 1, *INDEX*, 4 )' )

  f = parse( 'x: 4\n#a: testfunc( x, 2, 3 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 20 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 20 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( *INDEX*, 2, 3 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 5 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 50 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  function_map[ 'testfunc' ] = 'testfunc_{ID} - {1}'
  function_init_map[ 'testfunc' ] = """  global testfunc_{ID}
  val1 = {0}
  val2 = {2}
  if isinstance( val1, list ) and isinstance( val2, list ):
    testfunc_{ID} = sum( [ val1[ i ] + val2[ i ] for i in range( 0, len( val1 ) ) ] )
  elif isinstance( val1, list ):
    testfunc_{ID} = sum( [ i + val2 for i in val1 ] )
  elif isinstance( val2, list ):
    testfunc_{ID} = sum( [ val1 + i for i in val2 ] )
  else:
    testfunc_{ID} = val1 + val2
"""
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( 1, 7, x )' )
  with pytest.raises( ValueError ):
    parse( 'x: 10\n#a: testfunc( x, 2, 4 )' )
  with pytest.raises( ValueError ):
    parse( '#a: testfunc( 1, 7, *INDEX* )' )
  with pytest.raises( ValueError ):
    parse( '#a: testfunc( *INDEX*, 2, 4 )' )

  f = parse( 'x: 4\n#a: testfunc( 7, x, 9 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 12 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 12 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( 7, *INDEX*, 9 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 15 }
  assert f.code[ 'main' ]( 10, 1, 1, 0, 0, {} ) == { 'a': 6 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }


def test_multiinit_function():
  function_map[ 'testfunc' ] = 'testfunc_{ID}'
  function_init_map[ 'testfunc' ] = """  global testfunc_{ID}
  testfunc_{ID} = {0}
"""

  function_map[ 'testfunc2' ] = 'testfunc2_{ID}'
  function_init_map[ 'testfunc2' ] = """  global testfunc2_{ID}
  testfunc2_{ID} = {0} + 1
"""

  f = parse( '#a: testfunc( 3 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 3 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 3 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc2( 5 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 6 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 6 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: testfunc( 5 )\n#b: testfunc( 123 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 5, 'b': 123 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 5, 'b': 123 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ], 'b': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]  }

  f = parse( '#a: testfunc( 42 )\n#b: testfunc2( 19 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 42, 'b': 20 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 42, 'b': 20 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ], 'b': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]  }

  f = parse( '#a: testfunc2( 1 )\n#b: testfunc2( 3 )' )
  f.code[ 'init' ]( 10, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 2, 'b': 4 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 2, 'b': 4 }
  f.setBuckets( 10, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ], 'b': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ]  }
