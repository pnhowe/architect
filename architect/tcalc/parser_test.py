import pytest

from architect.tcalc.parser import parse, lint, ParserError


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

  parse( 'a: not ( *INDEX* % 10 )' )

  parse( 'a: 5' )
  parse( '\na: 5' )
  parse( 'a: 5\n' )
  parse( '\n\na: 5\n\n' )

  assert lint( 'a: asdf()' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
    parse( 'a: asdf()' )

  assert lint( 'a: mult()' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
    parse( 'a: mult()' )

  assert lint( 'a: mult( a, b )' ) is None
  parse( 'a: mult( a, b )' )

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
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setBuckets( 5, [ 0 ], [ 0 ], [ 0 ] )
  with pytest.raises( ValueError ):
    f.evaluate()
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 1, 2, 3, 4 ] }

  f = parse( '#a: *INDEX*\n#b: *TOTAL*\n#c: *COST*' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 1, 'b': 1, 'c': 0 }
  f.setBuckets( 5, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 1, 2, 3, 4 ], 'b': [ 0, 1, 2, 3, 4 ], 'c': [] }

  f.setBuckets( 1, [ 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0 ], [ 0, 0, 0, 0, 0 ] )
  assert f.evaluate() == { 'a': [ 1, 2, 3, 4 ], 'b': [ 0, 1, 2, 3, 4 ], 'c': [] }

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
  f = parse( '#a: ( ( ( ( 2 * *INDEX* ) + ( 3 * *TOTAL* ) ) + ( ( 5 * *COST* ) + ( 7 * *AVAILABILITY* ) ) ) + ( 11 * *RELIABILITY* ) )' )
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 2 }
  assert f.code[ 'main' ]( 0, 1, 0, 0, 0, {} ) == { 'a': 3 }
  assert f.code[ 'main' ]( 0, 0, 1, 0, 0, {} ) == { 'a': 5 }
  assert f.code[ 'main' ]( 0, 0, 0, 1, 0, {} ) == { 'a': 7 }
  assert f.code[ 'main' ]( 0, 0, 0, 0, 1, {} ) == { 'a': 11 }

  f.setBuckets( 3, [ 0, 0, 0 ], [ 0, 0, 0 ], [ 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8 ] }

  f.setBuckets( 3, [ -10, 0, -40 ], [ 0, 0, 0 ], [ 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 3, 4, 5 ] }


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
  f = parse( '#a: mult( 3, 5 )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 15 }
  f.setBuckets( 2, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1 ] }

  f = parse( 'x: 10\ny: 2\n#a: mult( x, y )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 20 }
  f.setBuckets( 2, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1 ] }

  f = parse( '#a: mult( *INDEX*, 1.2 )' )
  assert f.code[ 'main' ]( 1, 1, 0, 0, 0, {} ) == { 'a': 1.2 }
  assert f.code[ 'main' ]( 10, 1, 0, 0, 0, {} ) == { 'a': 12 }
  f.setBuckets( 2, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 1 ] }
