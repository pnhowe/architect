import pytest
import math

from architect.tcalc.parser import parse

# TODO: Deal with None values


def test_perodic():
  f = parse( '#a: periodic( *INDEX*, 10 )' )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': 0 }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 2, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': 10 }
  f.setBuckets( 100, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90 ] }


def test_linear():
  f = parse( '#a: linear( *INDEX*, 10 )' )
  f.code[ 'init' ]( 100, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 0, 100, 0, 0, 0, {} ) == { 'a': 0 }
  assert f.code[ 'main' ]( 1, 100, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 2, 100, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 10, 100, 0, 0, 0, {} ) == { 'a': 10 }
  f.setBuckets( 100, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90 ] }

  f = parse( 'a: linear( *INDEX*, 101 )' )
  f.setBuckets( 100, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  with pytest.raises( ValueError ):
    assert f.evaluate()

  parse( 'a: linear( *INDEX*, 0 )' )
  f.setBuckets( 100, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  with pytest.raises( ValueError ):
    assert f.evaluate()

  BUCKET_COUNT = 100
  for COUNT in range( 1, BUCKET_COUNT ):
    ref = [ math.ceil( i * ( BUCKET_COUNT / COUNT ) ) for i in range( 0, COUNT ) ]
    f = parse( '#a: linear( *INDEX*, {0} )'.format( COUNT ) )
    f.setBuckets( 100, [ 0 ], [ 0 ], [ 0 ] )
    f.setTimeSeriesValues( {} )
    assert f.evaluate()[ 'a' ] == ref


def test_weighted():
  f = parse( '#a: weighted( *INDEX*, 3, *COST* )' )
  f.setBuckets( 20, [ 0, 2, 1, 0 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 20, 30, 40 ] }

  f = parse( '#a: weighted( *INDEX*, 3, *COST* )' )
  f.setBuckets( 20, [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 27, 54 ] }

  f = parse( '#a: weighted( *INDEX*, 3, *COST* )' )
  f.setBuckets( 20, [ 0, 0, 0 ], [ 0, 0, 0 ], [ 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 20, 40 ] }

  for count, target_list in (
                   ( 1, [ 20 ] ),
                   ( 2, [ 20, 40 ] ),
                   ( 3, [ 20, 30, 40 ] ),
                   ( 4, [ 20, 26, 33, 40 ] ),
                   ( 5, [ 20, 26, 33, 40, 50 ] ),
                   ( 6, [ 20, 25, 30, 35, 40, 50 ] ),
                   ( 7, [ 20, 24, 28, 32, 36, 40, 50 ] ),
                   ( 8, [ 20, 24, 28, 32, 36, 40, 46, 53 ] ),
                   ( 9, [ 20, 23, 26, 30, 33, 36, 40, 46, 53 ] ),
                   ( 10, [ 20, 22, 25, 28, 31, 34, 37, 40, 46, 53 ] ),
                  ):
    f = parse( '#a: weighted( *INDEX*, {0}, *COST* )'.format( count ) )
    f.setBuckets( 20, [ 0, 2, 1, 0 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
    f.setTimeSeriesValues( {} )
    assert f.evaluate() == { 'a': target_list }

  for count, target_list in (
                   ( 1, [ 40 ] ),
                   ( 2, [ 20, 40 ] ),
                   ( 3, [ 20, 40, 50 ] ),
                   ( 4, [ 20, 30, 40, 50  ] ),
                   ( 5, [ 20, 30, 40, 46, 53 ] ),
                   ( 6, [ 20, 26, 33, 40, 46, 53 ] ),
                   ( 7, [ 20, 26, 33, 40, 45, 50, 55 ] ),
                   ( 8, [ 20, 25, 30, 35, 40, 45, 50, 55 ] ),
                   ( 9, [ 20, 25, 30, 35, 40, 44, 48, 52, 56 ] ),
                   ( 10, [ 20, 24, 28, 32, 36, 40, 44, 48, 52, 56 ] ),
                  ):
    f = parse( '#a: weighted( *INDEX*, {0}, *COST* )'.format( count ) )
    f.setBuckets( 20, [ 0, 1, 1, 0 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
    f.setTimeSeriesValues( {} )
    assert f.evaluate() == { 'a': target_list }

  f = parse( '#a: weighted( *INDEX*, 5, *COST* )' )
  f.setBuckets( 5, [ 10, 0, 0, 0 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4 ] }

  f = parse( '#a: weighted( *INDEX*, 5, *COST* )' )
  f.setBuckets( 10, [ 10, 0, 0, 0 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 2, 4, 6, 8 ] }

  f = parse( '#a: weighted( *INDEX*, 5, *COST* )' )
  f.setBuckets( 5, [ 0, 0, 0, 10 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 15, 16, 17, 18, 19 ] }

  f = parse( '#a: weighted( *INDEX*, 5, *COST* )' )
  f.setBuckets( 10, [ 0, 0, 0, 10 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 30, 32, 34, 36, 38 ] }

  f = parse( '#a: weighted( *INDEX*, 5, ( 1 / *COST* ) )' )
  f.setBuckets( 20, [ 0.1, 2, 1, 0.1 ], [ 0, 0, 0, 0 ], [ 0, 0, 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 10, 40, 60, 70 ] }

  f = parse( '#a: weighted( *INDEX*, 10, ( 1 / *COST* ) )' )
  f.setBuckets( 50, [ 2.0, 0.1 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 50, 55, 60, 65, 70, 75, 80, 85, 90, 95 ] }

  f = parse( '#a: weighted( *INDEX*, 10, ( 1 / *COST* ) )' )
  f.setBuckets( 50, [ 0.1, 2.0 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 5, 10, 15, 20, 25, 30, 35, 40, 45 ] }

  f = parse( '#a: weighted( *INDEX*, 10, ( 1 / *COST* ) )' )
  f.setBuckets( 50, [ 1.0, 1.0 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90 ] }

  f = parse( '#a: weighted( *INDEX*, 10, ( 1 / *COST* ) )' )
  f.setBuckets( 50, [ 2.0, 1.0 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 16, 33, 50, 57, 64, 71, 78, 85, 92 ] }

  f = parse( '#a: weighted( *INDEX*, 10, *COST* )' )
  f.setBuckets( 50, [ 1000.0, 0.001 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 5, 10, 15, 20, 25, 30, 35, 40, 45 ] }

  f = parse( '#a: weighted( *INDEX*, 10, *COST* )' )
  f.setBuckets( 50, [ 0.001, 1000.0 ], [ 0, 0 ], [ 0, 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 50, 55, 60, 65, 70, 75, 80, 85, 90, 95 ] }


def test_above_below_functions():
  f = parse( '#a: above( *INDEX*, 10 )' )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 11, 0, 0, 0, 0, {} ) == { 'a': 11 }
  f.setBuckets( 20, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 11, 12, 13, 14, 15, 16, 17, 18, 19 ] }

  f = parse( '#a: below( *INDEX*, 10 )' )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': 0 }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 1 }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 11, 0, 0, 0, 0, {} ) == { 'a': False }
  f.setBuckets( 20, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 ] }

  f = parse( '#a: above_inclusive( *INDEX*, 10 )' )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': 10 }
  assert f.code[ 'main' ]( 11, 0, 0, 0, 0, {} ) == { 'a': 11 }
  f.setBuckets( 20, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ] }

  f = parse( '#a: below_inclusive( *INDEX*, 10 )' )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': 0 }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': 1 }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': 10 }
  assert f.code[ 'main' ]( 11, 0, 0, 0, 0, {} ) == { 'a': False }
  f.setBuckets( 20, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ] }

  f = parse( """i: periodic( *INDEX*, 10 )
#a: above_inclusive( i, 30 )
#b: below( i, 30 )""" )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': False, 'b': 0 }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': False, 'b': False }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': False, 'b': 10 }
  assert f.code[ 'main' ]( 30, 0, 0, 0, 0, {} ) == { 'a': 30, 'b': False }
  assert f.code[ 'main' ]( 50, 0, 0, 0, 0, {} ) == { 'a': 50, 'b': False }
  f.setBuckets( 100, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 30, 40, 50, 60, 70, 80, 90 ], 'b': [ 0, 10, 20 ] }


def test_filter_functions():
  f = parse( '#a: filter( *INDEX*, ( *INDEX* > 10 ) )' )
  f.code[ 'init' ]( 20, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 11, 0, 0, 0, 0, {} ) == { 'a': 11 }
  f.setBuckets( 20, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 11, 12, 13, 14, 15, 16, 17, 18, 19 ] }

  f = parse( '#a: filter( linear( *INDEX*, 4 ), ( *INDEX* >= 10 ) )' )
  f.code[ 'init' ]( 20, [ 0 ], [ 0 ], [ 0 ], {} )
  assert f.code[ 'main' ]( 0, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 1, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 5, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 10, 0, 0, 0, 0, {} ) == { 'a': 10 }
  assert f.code[ 'main' ]( 11, 0, 0, 0, 0, {} ) == { 'a': False }
  assert f.code[ 'main' ]( 15, 0, 0, 0, 0, {} ) == { 'a': 15 }
  f.setBuckets( 20, [ 0 ], [ 0 ], [ 0 ] )
  f.setTimeSeriesValues( {} )
  assert f.evaluate() == { 'a': [ 10, 15 ] }
