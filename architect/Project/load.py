import os
import string
import toml
import re


hostname_regex = re.compile( '^[a-z0-9][a-z0-9\-]*[a-z0-9]$' )
name_regex = re.compile( '^[a-zA-Z0-9][a-zA-Z0-9_\-]*$' )
item_list = ( 'address_block', 'structure', 'complex', 'plan' )


SITE_PATTERN = {
                 'description': str,
                 'parent': ( str, None ),
                 'config_values': ( dict, {} )
               }

ADDRESSBLOCK_PATTERN = {
                        'subnet': str,
                        'prefix': int,
                        'gateway_offset': ( int, None ),
                        'reserved_offset_list': [ int ],
                        'dynamic_offset_list': [ int ]
                       }


STRUCTURE_PATTERN = {
                      'address_list': [ { 'address_block': str, 'offset': int } ],
                      'type': str,
                      'config_values': ( dict, None )
                   }

STRUCTURE_PATTERN_MAP = {
                          'Manual': { 'blueprint': str },
                          'AMT': { 'blueprint': str, 'amt_interface': { 'mac': str, 'offset': int } },
                          'VCenter': { 'blueprint': str, 'complex': str },
                          'Docker': { 'blueprint': str, 'complex': str }
                         }

COMPLEX_PATTERN = {
                    'type': str,
                    'description': str,
                    'built_percentage': ( int, None ),
                    'member_list': [ str ]
                  }

COMPLEX_PATTERN_TYPED = {
                          'Manual': {},
                          'VCenter': {
                                         'host': str,
                                         'username': str,
                                         'password': str,
                                         'datacenter': ( 'str', 'ha-datacenter' ),
                                         'cluster': ( 'str', 'localhost.' )
                                     }
                        }

PLAN_PATTERN = {
                 'description': str,
                 'script': str,
                 'address_block': str,
                 'complex_list': ( list, [] ),
                 'blueprint_map': ( dict, {} ),
                 'timeseries_map': dict,
                 'enabled': ( bool, None ),
                 'change_cooldown': ( int, None ),
                 'config_values': ( dict, {} ),
                 'max_inflight': ( int, None ),
                 'hostname_pattern': ( str, None ),
                 'slots_per_complex': ( int, None ),
                 'can_move': ( bool, None ),
                 'can_destroy': ( bool, None ),
                 'can_build': ( bool, None )
               }


def _sub_load( filepath, paramater_map ):
  template = string.Template( open( filepath, 'r' ).read() )
  config = toml.loads( template.substitute( paramater_map ) )

  result = {}
  for item in item_list:
    try:
      result[ item ] = config[ item ]
    except KeyError:
      result[ item ] = {}

  return result


def _sub_find_load( filename, paramater_map, project_path ):
  filepath = os.path.join( project_path, filename ) + '.toml'
  if os.path.isfile( filepath ):
    return _sub_load( filepath, paramater_map )

  raise ValueError( 'Unable to find include "{0}"'.format( filename ) )


def _fix_types( data ):
  if isinstance( data, dict ):
    for key, value in data.items():
      if type( value ).__name__ == 'DynamicInlineTableDict':
        data[ key ] = dict( value )

      _fix_types( value )

  elif isinstance( data, list ):
    for index in range( 0, len( data ) ):
      value = data[ index ]
      if type( value ).__name__ == 'DynamicInlineTableDict':
        data[ index ] = dict( value )

      _fix_types( value )

  elif isinstance( data, ( str, int ) ):
    return

  else:
    raise ValueError( 'Unknown type "{0}"'.format( type( data ).__name__ ) )


def loadProject( project_path ):
  config = toml.load( os.path.join( project_path, 'architect.toml' ) )
  site_map = {}
  plan_map = {}

  for name in config[ 'site' ]:
    site = config[ 'site' ][ name ]
    site_map[ name ] = site
    for item in item_list:
      try:
        site_map[ name ][ item ] = config[ item ][ name ]
      except KeyError:
        site_map[ name ][ item ] = {}

    for filename, paramater_map in site.get( '__include__', {} ).items():
      paramater_map[ 'site' ] = name
      for item in item_list:
        sub = _sub_find_load( filename, paramater_map, project_path )
        site_map[ name ][ item ].update( sub[ item ] )

    try:
      del site[ '__include__' ]
    except KeyError:
      pass

  for name in config.get( 'plan', [] ):
    plan = config[ 'plan' ][ name ]
    plan_map[ name ] = plan

  _fix_types( site_map )
  _fix_types( plan_map )

  return { 'sites': site_map, 'plans': plan_map }


def _validate_item( location, item, pattern ):
  itype = type( item )

  if isinstance( pattern, type ):
    rtype = pattern
  else:
    rtype = type( pattern )

  if itype != rtype:
    raise ValueError( '"{0}", is the wrong type, expected "{1}", got "{2}"'.format( location, rtype.__name__, itype.__name__ ) )

  if isinstance( pattern, type ):  # the pattern dosen't have any children to iterate into
    return

  if rtype == dict:
    for name, sub_pattern in pattern.items():
      if isinstance( sub_pattern, tuple ):
        try:
          _validate_item( '{0}.{1}'.format( location, name ), item[ name ], sub_pattern[0] )
        except KeyError:
          if sub_pattern[1] is not None:
            item[ name ] = sub_pattern[1]

      else:
        try:
          _validate_item( '{0}.{1}'.format( location, name ), item[ name ], sub_pattern )
        except KeyError:
          raise ValueError( '"{0}" missing from "{1}"'.format( name, location ) )

  elif rtype == list:
    for row in item:
      _validate_item( location, row, pattern[0] )


def validateProject( project ):
  for site, value_map in project[ 'sites' ].items():
    if not name_regex.match( site ):
      raise ValueError( 'Invalid Site Name "{0}"'.format( site ) )

    _validate_item( 'site.{0}'.format( site ), value_map, SITE_PATTERN )

    for uid in value_map[ 'address_block' ]:
      _validate_item( 'address_block.{0}.{1}'.format( site, uid ), value_map[ 'address_block' ][ uid ], ADDRESSBLOCK_PATTERN )

    for hostname in value_map[ 'structure' ]:
      if not hostname_regex.match( hostname ):
        raise ValueError( 'Invalid hostname "{0}" in "{1}"'.format( hostname, site ) )

      _validate_item( 'structure.{0}.{1}'.format( site, hostname ), value_map[ 'structure' ][ hostname ], STRUCTURE_PATTERN )

      try:
        ftype = value_map[ 'structure' ][ hostname ][ 'type' ]
      except KeyError:
        raise ValueError( 'structure "{0}" in "{1}" missing type'.format( hostname, site ) )

      _validate_item( 'structure.{0}.{1}'.format( site, hostname ), value_map[ 'structure' ][ hostname ], STRUCTURE_PATTERN_MAP[ ftype ] )

    for complex in value_map[ 'complex' ]:
      _validate_item( 'complex.{0}.{1}'.format( site, complex ), value_map[ 'complex' ][ complex ], COMPLEX_PATTERN )
      item_type = value_map[ 'complex' ][ complex ][ 'type' ]
      if item_type not in COMPLEX_PATTERN_TYPED.keys():
        raise ValueError( 'Complex Type "{0}" not valid'.format( item_type ) )

      _validate_item( 'complex.{0}.{1}'.format( site, complex ), value_map[ 'complex' ][ complex ], COMPLEX_PATTERN_TYPED[ item_type ] )

  for plan, value_map in project[ 'plans' ].items():
    _validate_item( 'plan.{0}'.format( plan ), value_map, PLAN_PATTERN )
