import hashlib
from datetime import datetime, timezone
from django.apps import apps


def _compare_item( a, b, name ):
  a_type = type( a )

  if a is not None and a_type != type( b ):
    raise ValueError( 'types do not match, "{0}" and "{1}" for "{2}"'.format( a_type.__name__, type( b ).__name__, name ) )

  if a_type == list:
    if len( a ) != len( b ):
      return True

    tmp_a = sorted( a, key=str )
    tmp_b = sorted( b, key=str )
    if [ 1 for i in range( 0, len( a ) ) if _compare_item( tmp_a[ i ], tmp_b[ i ], name ) ]:
      return True

  elif a_type == dict:
    if set( a ) != set( b ):  # compare keys
      return True

    elif [ 1 for key in a.keys() if _compare_item( a[ key ], b[ key ], name ) ]:  # compare values
      return True

  else:
    if a != b:
      return True

  return False


def _compare( current, project, name_list ):
  result = []
  for name in name_list:
    try:
      current_val = current[ name ]
    except KeyError:
      raise ValueError( 'name "{0}" not found in current set'.format( name ) )

    try:
      project_val = project[ name ]
    except KeyError:
      continue  # we can skip if it's not the project
      # raise ValueError( 'name "{0}" not found in project set'.format( name ) )

    if _compare_item( current_val, project_val, name ):
      result.append( name )

  return result


class ProjectComparer():
  def __init__( self, project, contractor ):
    self.site_map = project[ 'sites' ]
    self.plan_map = project[ 'plans' ]
    self.contractor = contractor
    self.change_list = []
    self.message = None

  @property
  def change( self ):
    return self.change_list

  def compare( self ):
    Site = apps.get_model( 'Project', 'Site' )
    self.change_list = []

    local_site_list = set( Site.objects.all().values_list( 'name', flat=True ) )
    project_site_list = set( self.site_map.keys() )

    for site_name in local_site_list - project_site_list:
      self.change_list.append( { 'type': 'site', 'action': 'local_delete', 'target_id': site_name } )

    for site_name in project_site_list - local_site_list:
      self.change_list.append( { 'type': 'site', 'action': 'local_create', 'target_id': site_name } )

    if self.change_list:
      self.message = 'Local Site Add/Remove'
      return True

    remote_site_list = set( self.contractor.getSiteList() )
    for site_name in remote_site_list - local_site_list:
      self.change_list.append( { 'type': 'site', 'action': 'remote_delete', 'target_id': site_name } )

    for site_name in local_site_list - remote_site_list:
      project_site = self.site_map[ site_name ]
      self.change_list.append( { 'type': 'site', 'action': 'remote_create', 'target_id': site_name, 'target_val': { 'description': project_site[ 'description' ], 'config_values': project_site[ 'config_values' ] } } )

    if self.change_list:
      self.message = 'Remote Site Add/Remove'
      return True

    for site_name in project_site_list:
      local_site = Site.objects.get( name=site_name )
      project_site = self.site_map[ site_name ]

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
      self.message = 'Resource Changes'
      return True

    if self._plan( self.plan_map ):
      self.message = 'Plan Changes'
      return True

    else:
      return False

  def _site( self, project_site, local_site, remote_site ):
    # update site details
    change_list = _compare( remote_site, project_site, ( 'description', 'parent', 'config_values' ) )
    if change_list:
      self.change_list.append( { 'type': 'site', 'action': 'change', 'target_id': local_site.name, 'current_val': dict( [ ( i, remote_site[ i ] ) for i in change_list ] ), 'target_val': dict( [ ( i, project_site[ i ] ) for i in change_list ] ) } )
      return True

    if self._addressBlock( project_site, local_site ):
      return True

    if self._complex( project_site, local_site ):
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
    for block_name in remote_address_block_list - project_address_block_list:
      self.change_list.append( { 'type': 'address_block', 'action': 'remote_delete', 'site': local_site, 'target_id': remote_address_block_map[ block_name ][ 'id' ] } )
      dirty = True

    for block_name in project_address_block_list - remote_address_block_list:
      project_address_block = project_site[ 'address_block' ][ block_name ]
      self.change_list.append( { 'type': 'address_block', 'action': 'remote_create', 'site': local_site, 'target_id': block_name, 'target_val': project_address_block } )
      dirty = True

    if dirty:
      return

    # update address block details
    for block_name, remote_address_block in remote_address_block_map.items():
      project_address_block = project_site[ 'address_block' ][ block_name ]
      change_list = _compare( remote_address_block, project_address_block, ( 'name', 'subnet', 'prefix', 'gateway_offset', 'reserved_offset_list', 'dynamic_offset_list' ) )

      if change_list:
        self.change_list.append( { 'type': 'address_block', 'action': 'change', 'site': local_site, 'target_id': remote_address_block[ 'id' ],
                                   'current_val': dict( [ ( i, list( remote_address_block[ i ] ) ) for i in change_list ] ),
                                   'target_val': dict( [ ( i, project_address_block[ i ] ) for i in change_list ] )
                                   } )
        dirty = True

    return dirty

  def _structure( self, project_site, local_site ):
    dirty = False
    project_structure_list = set( project_site[ 'structure' ].keys() )

    local_instance_list = set( local_site.instance_set.all().values_list( 'hostname', flat=True ) )

    # create/destroy structures
    remote_structure_map = self.contractor.getStructureMap( local_site.name )
    remote_structure_list = set( remote_structure_map.keys() )

    for structure_name in remote_structure_list - project_structure_list - local_instance_list:
      self.change_list.append( { 'type': 'structure', 'action': 'remote_delete', 'site': local_site, 'target_id': structure_name } )
      dirty = True

    for structure_name in project_structure_list - remote_structure_list:
      project_structure = project_site[ 'structure' ][ structure_name ]
      self.change_list.append( { 'type': 'structure', 'action': 'remote_create', 'site': local_site, 'target_id': structure_name, 'target_val': project_structure } )
      dirty = True

    if dirty:
      return True

    # update structure details
    for structure_name, remote_structure in remote_structure_map.items():
      if structure_name in local_instance_list:
        continue

      project_structure = project_site[ 'structure' ][ structure_name ]
      change_list = _compare( remote_structure, project_structure, ( 'blueprint', 'type', 'address_list', 'config_values' ) )

      if change_list:
        self.change_list.append( { 'type': 'structure', 'action': 'change', 'site': local_site, 'target_id': structure_name,
                                   'current_val': dict( [ ( i, remote_structure[ i ] ) for i in change_list ] ),
                                   'target_val': dict( [ ( i, project_structure[ i ] ) for i in change_list ] )
                                   } )
        dirty = True

    return dirty

  def _complex( self, project_site, local_site ):
    Complex = apps.get_model( 'Contractor', 'Complex' )
    dirty = False

    # create/destroy complexes locally
    local_complex_list = set( Complex.objects.filter( site=local_site ).values_list( 'name', flat=True ) )
    project_complex_list = set( project_site[ 'complex' ].keys() )

    for complex_name in project_complex_list - local_complex_list:
      self.change_list.append( { 'type': 'complex', 'action': 'local_create', 'site': local_site, 'target_id': complex_name } )
      dirty = True

    for complex_name in local_complex_list - project_complex_list:
      self.change_list.append( { 'type': 'complex', 'action': 'local_delete', 'site': local_site, 'target_id': complex_name } )
      dirty = True

    if dirty:
      return True

    # create/destroy complexes remotely
    remote_complex_map = self.contractor.getComplexMap( local_site.name )
    remote_complex_list = set( remote_complex_map.keys() )
    for complex_name in remote_complex_list - local_complex_list:
      self.change_list.append( { 'type': 'complex', 'action': 'remote_delete', 'site': local_site, 'target_id': complex_name } )
      dirty = True

    for complex_name in local_complex_list - remote_complex_list:
      project_complex = project_site[ 'complex' ][ complex_name ]
      self.change_list.append( { 'type': 'complex', 'action': 'remote_create', 'site': local_site, 'target_id': complex_name, 'target_val': project_complex } )
      dirty = True

    if dirty:
      return True

    # update complex details
    for complex_name, remote_complex in remote_complex_map.items():
      project_complex = project_site[ 'complex' ][ complex_name ]
      change_list = _compare( remote_complex, project_complex, ( 'description', 'type', 'built_percentage', 'member_list' ) )

      if change_list:
        self.change_list.append( { 'type': 'complex', 'action': 'change', 'site': local_site, 'target_id': complex_name,
                                   'current_val': dict( [ ( i, remote_complex[ i ] ) for i in change_list ] ),
                                   'target_val': dict( [ ( i, project_complex[ i ] ) for i in change_list ] )
                                   } )
        dirty = True

    return dirty

  def _plan( self, project_plan ):
    Plan = apps.get_model( 'Plan', 'Plan' )
    dirty = False

    # create/destroy plans
    local_plan_list = set( Plan.objects.all().values_list( 'name', flat=True ) )
    project_plan_list = set( project_plan.keys() )

    for plan_name in project_plan_list - local_plan_list:
      project_plan = project_plan[ plan_name ]
      self.change_list.append( { 'type': 'plan', 'action': 'local_create', 'target_id': plan_name, 'target_val': project_plan } )
      dirty = True

    for complex_name in local_plan_list - project_plan_list:
      self.change_list.append( { 'type': 'plan', 'action': 'local_delete', 'target_id': plan_name } )
      dirty = True

    if dirty:
      return True

    # update plan details
    for plan_name in project_plan_list:
      project_plan = project_plan[ plan_name ]
      local_plan_obj = Plan.objects.get( name=plan_name )

      local_plan = local_plan_obj.__dict__
      local_plan[ 'complex_list' ] = [ i.name for i in local_plan_obj.complex_list.all() ]
      local_plan[ 'blueprint_map' ] = dict( [ ( i.script_name, i.blueprint.name ) for i in local_plan_obj.planblueprint_set.all() ] )
      local_plan[ 'timeseries_map' ] = dict( [ ( i.script_name, i.timeseries.metric ) for i in local_plan_obj.plantimeseries_set.all() ] )

      change_list = _compare( local_plan, project_plan, ( 'description', 'complex_list', 'blueprint_map', 'timeseries_map', 'enabled', 'change_cooldown', 'config_values', 'max_inflight', 'hostname_pattern', 'script', 'slots_per_complex', 'can_move', 'can_destroy', 'can_build' ) )
      if change_list:
        self.change_list.append( { 'type': 'plan', 'action': 'change', 'target_id': plan_name,
                                   'current_val': dict( [ ( i, local_plan[ i ] ) for i in change_list ] ),
                                   'target_val': dict( [ ( i, project_plan[ i ] ) for i in change_list ] )
                                   } )
        dirty = True

    return dirty
