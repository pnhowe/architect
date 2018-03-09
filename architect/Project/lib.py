import os
import string
import toml
import re


hostname_regex = re.compile( '^[a-z0-9][a-z0-9\-]*[a-z0-9]$' )
name_regex = re.compile( '^[a-zA-Z0-9][a-zA-Z0-9_\-]*$' )
item_list = ( 'address_block', 'instance', 'complex' )


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


def _prep_paramaters( paramater_map ):
  for name in paramater_map:
    if isinstance( paramater_map[ name ], str ):
      paramater_map[ name ] = '\'{0}\''.format( paramater_map[ name ] )


def loadProject( project_path ):
  config = toml.load( os.path.join( project_path, 'architect.toml' ) )
  result = {}
  site_list = []

  for name in config[ 'site' ]:
    site = config[ 'site' ][ name ]
    site_list.append( name )
    result[ name ] = site
    for item in item_list:
      try:
        result[ name ][ item ] = config[ item ][ name ]
      except KeyError:
        result[ name ][ item ] = {}

    for filename, paramater_map in site.get( '__include__', {} ).items():
      paramater_map[ 'site' ] = name
      _prep_paramaters( paramater_map )
      for item in item_list:
        sub = _sub_find_load( filename, paramater_map, project_path )
        result[ name ][ item ].update( sub[ item ] )

    try:
      del site[ '__include__' ]
    except KeyError:
      pass

  return ( list( set( site_list ) ), result )

ADDRESSBLOCK_PATTERN = {
                        'subnet': str,
                        'prefix': int,
                        'gateway_offset': int,
                        'reserved_offset_list': [ int ],
                        'dynamic_offset_list': [ int ]
                       }


INSTANCE_PATTERN = {
                      'address_list': [ { 'address_block': int, 'offset': int } ],
                      'type': str
                   }

INSTANCE_PATTERN_MAP = {
                          'Manual': { 'blueprint': str },
                          'AMT': { 'blueprint': str, 'amt_interface': { 'mac': str, 'offset': int } },
                          'Vcenter': { 'blueprint': str, 'complex': str },
                          'Docker': { 'blueprint': str, 'complex': str }
                         }

COMPLEX_PATTERN = {
                    'type': str,
                    'member_list': [ str ],
                  }


def _validate_item( location, item, pattern ):
  itype = type( item )

  if itype.__name__ == 'DynamicInlineTableDict':
    itype = dict

  if isinstance( pattern, type ):
    rtype = pattern
  else:
    rtype = type( pattern )

  if itype != rtype:
    raise ValueError( '"{0}", is the wrong type, expected "{2}", got "{3}"'.format( location, rtype.__name__, itype.__name__ ) )

  if rtype == dict:
    for name, sub_pattern in pattern.items():
      try:
        _validate_item( '{0}.{1}'.format( location, name ), item[ name ], sub_pattern )
      except KeyError:
        raise ValueError( '"{0}" missing from "{1}"'.format( name, location ) )

  elif rtype == list:
    for row in item:
      _validate_item( location, row, pattern[0] )


def validateProject( config ):
  for site in config:
    if not name_regex.match( site ):
      raise ValueError( 'Invalid Site Name "{0}"'.format( site ) )

    for uid in config[ site ][ 'address_block' ]:
      _validate_item( 'address_block.{0}.{1}'.format( site, uid ), config[ site ][ 'address_block' ][ uid ], ADDRESSBLOCK_PATTERN )

    for hostname in config[ site ][ 'instance' ]:
      if not hostname_regex.match( hostname ):
        raise ValueError( 'Invalid hostname "{0}" in "{1}"'.format( hostname, site ) )

      _validate_item( 'instance.{0}.{1}'.format( site, hostname ), config[ site ][ 'instance' ][ hostname ], INSTANCE_PATTERN )

      try:
        ftype = config[ site ][ 'instance' ][ hostname ][ 'type' ]
      except KeyError:
        raise ValueError( 'Instance "{0}" in "{1}" missing type'.format( hostname, site ) )

      _validate_item( 'instance.{0}.{1}'.format( site, hostname ), config[ site ][ 'instance' ][ hostname ], INSTANCE_PATTERN_MAP[ ftype ] )


def diffStaticPlan( old, new ):
  result = {}
  for item in item_list:
    try:
      old_items = set( old[ item ].keys() )
    except KeyError:
      old_items = set( [] )
    new_items = set( new[ item ].keys() )

    result[ item ] = {}
    result[ item ][ 'adding' ] = list( new_items - old_items )
    result[ item ][ 'removing' ] = list( old_items - new_items )

  return result
