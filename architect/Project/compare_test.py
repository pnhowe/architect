import pytest

from architect.Project.compare import _compare


def test_compare():
  assert _compare( {}, {}, [] ) == []

  assert _compare( { 'a': 1 }, { 'a': 2 }, [] ) == []

  assert _compare( { 'a': 1 }, { 'a': 2 }, [ 'a' ] ) == [ 'a' ]

  with pytest.raises( ValueError ):
    assert _compare( { 'a': 1 }, { 'a': '1' }, [ 'a' ] )

  with pytest.raises( ValueError ):
    assert _compare( { 'a': 1 }, { 'a': 'b' }, [ 'a' ] )

  with pytest.raises( ValueError ):
    assert _compare( { 'a': 1 }, { 'a': [ 1 ] }, [ 'a' ] )

  assert _compare( { 'a': [ 1, 2, 3 ] }, { 'a': [ 1, 2, 3 ] }, [ 'a' ] ) == []
  assert _compare( { 'a': [ 1, 2, 3 ] }, { 'a': [ 3, 2, 1 ] }, [ 'a' ] ) == []
  assert _compare( { 'a': [ 3, 2, 1 ] }, { 'a': [ 1, 2, 3 ] }, [ 'a' ] ) == []
  assert _compare( { 'a': [ 1, 2, 3 ] }, { 'a': [ 1, 1 ] }, [ 'a' ] ) == [ 'a' ]
  assert _compare( { 'a': [ 1, 2, 3 ] }, { 'a': [ 1, 1, 1 ] }, [ 'a' ] ) == [ 'a' ]

  assert _compare( { 'a': { 'b': 1 } }, { 'a': { 'b': 1 } }, [ 'a' ] ) == []
  assert _compare( { 'a': { 'b': 1 } }, { 'a': { 'b': 2 } }, [ 'a' ] ) == [ 'a' ]
  assert _compare( { 'a': { 'b': 1 } }, { 'a': { 'b': 1, 'c': 1 } }, [ 'a' ] ) == [ 'a' ]
  assert _compare( { 'a': { 'c': 1, 'b': 1 } }, { 'a': { 'b': 1, 'c': 1 } }, [ 'a' ] ) == []
  assert _compare( { 'a': { 'b': 1, 'c': 1 } }, { 'a': { 'b': 1, 'c': 2 } }, [ 'a' ] ) == [ 'a' ]

  assert _compare( { 'a': { 'b': [ 1, 2, 3 ] } }, { 'a': { 'b': [ 1, 2, 3 ] } }, [ 'a' ] ) == []
  assert _compare( { 'a': { 'b': [ 1, 2, 3 ] } }, { 'a': { 'b': [ 3, 2, 1 ] } }, [ 'a' ] ) == []
  assert _compare( { 'a': { 'b': [ 3, 2, 1 ] } }, { 'a': { 'b': [ 1, 2, 3 ] } }, [ 'a' ] ) == []
  assert _compare( { 'a': { 'b': [ 1, 2, 3 ] } }, { 'a': { 'b': [ 1, 1, 2 ] } }, [ 'a' ] ) == [ 'a' ]
