import pytest

from architect.tcalc.parser import parse, lint, ParserError


def test_parse():
  assert lint( '' ) is None
  f = parse( '' )
  assert f.expected_variables == []

  assert lint( 'asd' ) is None
  f = parse( 'asd' )
  assert f.expected_variables == [ 'asd' ]

  assert lint( '42' ) is None
  f = parse( '42' )
  assert f.expected_variables == []

  assert lint( '*' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
    parse( '*' )

  f = parse( '( asd + zxc )' )
  assert sorted( f.expected_variables ) == [ 'asd', 'zxc' ]

  f = parse( '( asd + asd )' )
  assert f.expected_variables == [ 'asd' ]

  assert lint( 'asdf()' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
    parse( 'asdf()' )

  assert lint( 'scaled()' ) == 'Incomplete Parsing at column: 1'
  with pytest.raises( ParserError ):
      parse( 'scaled()' )

  assert lint( 'scaled( a, b )' ) is None
  f = parse( 'scaled( a, b )' )
  assert sorted( f.expected_variables ) == [ 'a', 'b' ]


def test_basic_evaluation():
  f = parse( '5' )
  assert f.expected_variables == []
  assert f.function( 1, {} ) == 5
  with pytest.raises( ValueError ):
    f.evaluate( 1 )
  f.setValues( {} )
  assert f.evaluate( 1 ) is True

  f = parse( 'x' )
  assert f.expected_variables == [ 'x' ]
  assert f.function( 1, { 'x': 42 } ) == 42
  with pytest.raises( ValueError ):
    f.evaluate( 1 )
  with pytest.raises( ValueError ):
    f.setValues( {} )
  f.setValues( { 'x': 3 } )
  assert f.evaluate( 1 ) is True
  f.setValues( { 'x': 0 } )
  assert f.evaluate( 1 ) is False

  f = parse( '( x + y )' )
  assert f.expected_variables == [ 'x', 'y' ]
  assert f.function( 1, { 'x': 42, 'y': 2 } ) == 44
  with pytest.raises( ValueError ):
    f.evaluate( 1 )
  with pytest.raises( ValueError ):
    f.setValues( {} )
  f.setValues( { 'x': 3, 'y': 3 } )
  assert f.evaluate( 1 ) is True
  f.setValues( { 'x': 3, 'y': -3 }  )
  assert f.evaluate( 1 ) is False

  f = parse( '( x + INDEX )' )
  assert f.expected_variables == [ 'x' ]
  assert f.function( 1, { 'x': 42 } ) == 43
  assert f.function( 5, { 'x': 42 } ) == 47
  with pytest.raises( ValueError ):
    f.evaluate( 1 )
  with pytest.raises( ValueError ):
    f.setValues( {} )
  f.setValues( { 'x': 3 } )
  assert f.evaluate( 1 ) is True
  f.setValues( { 'x': -3 }  )
  assert f.evaluate( 1 ) is True
  assert f.evaluate( 2 ) is True
  assert f.evaluate( 3 ) is False
  assert f.evaluate( 4 ) is True


def test_basic_function():
  f = parse( 'scaled( 3, 5 )' )
  assert f.expected_variables == []
  assert f.function( 1, {} ) == 15
  f.setValues( {} )
  assert f.evaluate( 0 ) is True
  assert f.evaluate( 1 ) is True

  f = parse( 'scaled( x, y )' )
  assert sorted( f.expected_variables ) == [ 'x', 'y' ]
  assert f.function( 1, { 'x': 10, 'y': 2 } ) == 20
  assert f.function( 1, { 'x': 3, 'y': 9 } ) == 27
  f.setValues( { 'x': 3, 'y': 9 }  )
  assert f.evaluate( 0 ) is True
  assert f.evaluate( 1 ) is True

  f = parse( 'scaled( INDEX, 1.2 )' )
  assert f.expected_variables == []
  assert f.function( 1, {} ) == 1.2
  assert f.function( 10, {} ) == 12
  f.setValues( {} )
  assert f.evaluate( 0 ) is False
  assert f.evaluate( 1 ) is True

  f = parse( 'pd( 5, INDEX, 2, INDEX )' )
  assert f.expected_variables == []
  assert f.function( 1, {} ) == 3
  assert f.function( 3, {} ) == 9
  f.setValues( {} )
  assert f.evaluate( 0 ) is False
  assert f.evaluate( 1 ) is True

  f = parse( 'pd( p, INDEX, d, INDEX )' )
  assert sorted( f.expected_variables ) == [ 'd', 'p' ]
  assert f.function( 1, { 'p': 10, 'd': 3.2 } ) == 6.8
  assert f.function( 2, { 'p': 10, 'd': 3.2 } ) == 13.6
  f.setValues( { 'p': 10, 'd': 3.2 } )
  assert f.evaluate( 0 ) is False
  assert f.evaluate( 1 ) is True


def test_count_functions():
  f = parse( 'scaled( x, y )' )
  assert f.function( 1, { 'x': 0, 'y': 0 } ) == 0
  assert f.function( 1, { 'x': 10, 'y': 2 } ) == 20
  assert f.function( 1, { 'x': 3, 'y': 9 } ) == 27
  assert f.function( 2, { 'x': 3, 'y': 9 } ) == 27
  f.setValues( { 'x': 3, 'y': 5 } )
  assert f.evaluate( 0 ) is True
  assert f.evaluate( 1 ) is True
  assert f.evaluate( 2 ) is True
  f.setValues( { 'x': 0, 'y': 0 } )
  assert f.evaluate( 0 ) is False
  assert f.evaluate( 1 ) is False
  assert f.evaluate( 2 ) is False

  f = parse( 'pd( p, v, d, v )' )
  assert f.function( 1, { 'p': 10, 'd': 3.2, 'v': 1 } ) == 6.8
  assert f.function( 20, { 'p': 10, 'd': 3.2, 'v': 1 } ) == 6.8
  f.setValues( { 'p': 1, 'd': 1, 'v': 1 } )
  assert f.evaluate( 0 ) is False
  assert f.evaluate( 1 ) is False
  f.setValues( { 'p': 1, 'd': 0, 'v': 1 } )
  assert f.evaluate( 0 ) is True
  assert f.evaluate( 1 ) is True


def test_distrubution_functions():
  f = parse( 'periodic( INDEX, p )' )
  f.setValues( { 'p': 10 } )
  assert f.evaluate( 1  ) is False
  assert f.evaluate( 10 ) is True

  f = parse( 'above( INDEX, p )' )
  f.setValues( { 'p': 10 } )
  assert f.evaluate( 1  ) is False
  assert f.evaluate( 10 ) is False
  assert f.evaluate( 11 ) is True

  f = parse( 'above( INDEX, p )' )
  value_list = []
  f.setValues( { 'p': 5 } )
  for i in range( 0, 10 ):
    value_list.append( f.evaluate( i ) )
  assert value_list == [ False, False, False, False, False, False, True, True, True, True ]
