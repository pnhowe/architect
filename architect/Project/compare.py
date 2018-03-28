from pprint import pprint
import hashlib
from datetime import datetime, timezone

from architect.Plan.models import Site


def _compare( a, b, name_list ):
  result = []
  for name in name_list:
    try:
      a_val = a[ name ]
    except KeyError:
      raise ValueError( 'name "{0}" not found in first set'.format( name ) )

    try:
      b_val = b[ name ]
    except KeyError:
      raise ValueError( 'name "{0}" not found in second set'.format( name ) )

    a_type = type( a_val )

    if a_type != type( b_val ):
      raise ValueError( 'types do not match, "{0}" and "{1}" for "{2}"'.format( a_type.__name__, type( b_val ).__name__, name ) )

    if a_type == list:
      if sorted( a_val ) != sorted( b_val ):
        result.append( name )

    else:
      if a_val != b_val:
        result.append( name )

  return result


class ProjectComparer():
  def __init__( self, project, contractor ):
    pprint( project )
    self.project = project
    self.contractor = contractor
    self.change_list = []
    self.message = None

  @property
  def changes( self ):
    return self.change_list.__iter__

  def compare( self ):
    self.change_list = []

    local_site_list = set( Site.objects.all().values_list( 'name', flat=True ) )
    project_site_list = set( self.project.keys() )

    for site_name in project_site_list - local_site_list:
      self.change_list.append( { 'type': 'site', 'action': 'local_create', 'target_id': site_name } )

    for site_name in local_site_list - project_site_list:
      self.change_list.append( { 'type': 'site', 'action': 'local_delete', 'target_id': site_name } )

    if self.change_list:
      self.message = 'Local Site Add/Remove'
      return True

    remote_site_list = set( self.contractor.getSiteList() )
    for site_name in local_site_list - remote_site_list:
      project_site = self.project[ site_name ]
      self.change_list.append( { 'type': 'site', 'action': 'remote_create', 'target_id': site_name, 'target_val': { 'description': project_site[ 'description' ], 'config_values': project_site[ 'config_values' ] } } )

    for site_name in remote_site_list - local_site_list:
      self.change_list.append( { 'type': 'site', 'action': 'remote_delete', 'target_id': site_name } )

    if self.change_list:
      self.message = 'Remote Site Add/Remove'
      return True

    for site_name in project_site_list:
      local_site = Site.objects.get( name=site_name )
      project_site = self.project[ site_name ]

      hasher = hashlib.sha1()
      hasher.update( str( project_site ).encode() )
      current_hash = hasher.hexdigest()
      if local_site.last_load_hash == current_hash:
        continue

      if self._site( project_site, local_site, self.contractor.getSite( site_name ) ):
        continue

      local_site.last_load = datetime.now( timezone.utc )
      local_site.last_load_hash = current_hash
      local_site.full_clean()
      local_site.save()

    if self.change_list:
      self.message = 'Changes'
      return True

    else:
      return False

  def _site( self, project_site, local_site, remote_site ):
    # first compare site values
    print( '***' )
    pprint( project_site )
    print( '----' )
    pprint( local_site )
    print( '~~~~' )
    pprint( remote_site )
    print( '===' )

    # update site details
    change_list = _compare( remote_site, project_site, ( 'description', 'config_values' ) )
    if change_list:
      self.change_list.append( { 'type': 'site', 'action': 'change', 'target_id': local_site.name, 'current_val': dict( [ ( i, remote_site[ i ] ) for i in change_list ] ), 'target_val': dict( [ ( i, project_site[ i ] ) for i in change_list ] ) } )
      return True

    if self._addressBlock( project_site, local_site ):
      return True

    if self._structure( project_site, local_site ):
      return True

    return False

  def _addressBlock( self, project_site, local_site ):
    dirty = False
    project_address_block_list = set( project_site[ 'address_block' ].keys() )

    # create/destroy the address blocks
    remote_address_block_map = self.contractor.getAddressBlockMap( local_site.name )
    remote_address_block_list = set( remote_address_block_map.keys() )
    for block_name in project_address_block_list - remote_address_block_list:
      address_block = project_site[ 'address_block' ][ block_name ]
      self.change_list.append( { 'type': 'address_block', 'action': 'remote_create', 'site': local_site, 'target_id': block_name, 'target_val': address_block } )
      dirty = True

    for block_name in remote_address_block_list - project_address_block_list:
      address_block = project_site[ 'address_block' ][ block_name ]
      self.change_list.append( { 'type': 'address_block', 'action': 'remote_delete', 'site': local_site, 'target_id': block_name } )
      dirty = True

    if dirty:
      return

    # update address block details
    for block_name, remote_address_block in remote_address_block_map.items():
      project_address_block = project_site[ 'address_block' ][ block_name ]
      change_list = _compare( remote_address_block, project_address_block, ( 'subnet', 'prefix', 'gateway_offset', 'reserved_offset_list', 'dynamic_offset_list' ) )

      if change_list:
        self.change_list.append( { 'type': 'address_block', 'action': 'change', 'site': local_site, 'target_id': block_name,
                                   'current_val': dict( [ ( i, list( remote_address_block[ i ] ) ) for i in change_list ] ),
                                   'target_val': dict( [ ( i, project_address_block[ i ] ) for i in change_list ] )
                                   } )
        dirty = True

    return dirty

  def _structure( self, project_site, local_site ):
    dirty = False
    project_structure_list = set( project_site[ 'structure' ].keys() )
    # third check structures

    # create/destroy structures
    remote_structure_map = self.contractor.getStructureMap( local_site.name )
    remote_structure_list = set( remote_structure_map.keys() )

    for structure_name in project_structure_list - remote_structure_list:
      structure = project_site[ 'structure' ][ structure_name ]
      self.change_list.append( { 'type': 'structure', 'action': 'remote_create', 'site': local_site, 'target_id': structure_name, 'target_val': structure } )
      dirty = True

    for structure_name in remote_structure_list - project_structure_list:
      structure = project_site[ 'structure' ][ structure_name ]
      self.change_list.append( { 'type': 'structure', 'action': 'remote_delete', 'site': local_site, 'target_id': structure_name } )
      dirty = True

    if dirty:
      return True

    # update structure details
    for structure_name, remote_structure in remote_structure_map.items():
      project_structure = project_site[ 'structure' ][ structure_name ]
      change_list = _compare( remote_structure, project_structure, ( 'blueprint', 'type', 'address_list' ) )

      if change_list:
        self.change_list.append( { 'type': 'structure', 'action': 'change', 'site': local_site, 'target_id': structure_name,
                                    'current_val': dict( [ ( i, remote_structure i ] ) for i in change_list ] ),
                                    'target_val': dict( [ ( i, project_structure[ i ] ) for i in change_list ] )
                                   } )
        dirty = True

    return dirty