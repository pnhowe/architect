tcalc Documentation
===================

Each line is a value assignment.  The format is::

  <name to assigne value to>: <value>

value can be another name, function call or expression

valid expressions are `^` (exponent/power), `*` (multiply), `/`(divide), `%` (modulas),
`+` (add), `-` (subtract), `&`(bitwise and), `|` (bitwise or), `and` (logical and),
`or` (locigal or), `==` (logical equal), `!=` (logical notequal),
`<=` (logical less than and equal), `>=` (logical greater than and equal),
`>` (logical greater than), `<` (logical less than) and must be encolused by
`( )`.  For example: `( a + 2 )`.  Expressions can be embded.  ie:
`( ( 1 + 2 ) / a )`.  Functions can also be included (NOTE: functions return a
boolean value), ie: `not ( periodic( *INDEX*, 3 ) % 2 )`

If the name is prefixed with a `#` the name is the name of the blueprint to assign
the value to.

If the name is prefixed with a `@`, the timeseries value is used in it's place.

Special names `*INDEX*`, `*TOTAL*`, `*COST*`, `*AVAILABILITY*`, `*RELIABILITY*`
are replaced by the curent slot INDEX, TOTAL slots, or COST, AVAILABILITY, RELIABILITY
value for that complex

Function Documentation
======================


Distrubution functions
----------------------

periodic( index, period ):
  Item every `period` slots

linear( index, count ):
  Evenly space `count` items

weighted( index, count, weight )

Subset functions
----------------

above, below, above_inclusive, below_inclusive, filter


Examples
--------

Item every 40 slots::

  #generic-manual-structure: periodic( *INDEX*, 40 )

Same thing can be acomplished with::

  #generic-manual-structure: not ( *INDEX* % 40 )

20 Items evenly distrubuted::

  #generic-manual-structure: linear( *INDEX*, 20 )

20 Items Weighted positivly with Availability Complex (ie: toward higher Availability)::

  #generic-manual-structure: weighted( *INDEX*, 20, *AVAILABILITY* )

20 Items Weighted negativly with Price Complex (ie: toward lower cost)::

  #generic-manual-structure: weighted( *INDEX*, 20, ( 1 / *COST* ) )

10 Items evenly distrubuted, with "AB" testing split at 30::

  items: liner( *INDEX*, 10 )
  #version1: above_inclusive( liner, 30 )
  #version2: below( liner, 30 )

Item every 40 slots, excepet where cost is more than 10::

  #generic-manual-structure: filter( periodic( *INDEX*, 40 ), ( *COST* < 10 ) )
