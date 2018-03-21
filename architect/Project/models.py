import os
import hashlib
from datetime import datetime, timezone

from pprint import pprint

from django.db import models
from django.conf import settings

from cinp.orm_django import DjangoCInP as CInP
from django.core.exceptions import ValidationError

from architect.Plan.models import Site
from architect.fields import JSONField

from architect.Project.lib import loadProject, validateProject
from architect.Contractor.libcontractor import getContractor

cinp = CInP( 'Project', '0.1', doc="""This is the loader for the Project as a whole
""" )

CHANGE_TYPE_CHOICES = ( 'site', 'address_block', 'instance' )
CHANGE_ACTION_CHOICES = ( 'local_create', 'remote_create', 'local_delete', 'remote_delete', 'change' )


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


@cinp.model( not_allowed_verb_list=[ 'DELETE', 'CREATE', 'UPDATE', 'LIST', 'GET' ] )
class Loader( models.Model ):

  @cinp.action( return_type='String' )
  @staticmethod
  def rescan():
    if not os.path.isfile( os.path.join( settings.PROJECT_PATH, 'architect.toml' ) ):
      return 'Unable to find project file'

    contractor = getContractor()

    project = loadProject( settings.PROJECT_PATH )

    try:
      validateProject( project )
    except ValueError as e:
      return 'Error Validating Project: "{0}"'.format( e )

    Change.objects.all().delete()

    pprint( project )

    local_site_list = set( Site.objects.all().values_list( 'name', flat=True ) )
    project_site_list = set( project.keys() )

    have_changes = False

    for site_name in project_site_list - local_site_list:
      change = Change( type='site', action='local_create', target_id=site_name )
      change.full_clean()
      change.save()
      have_changes = True

    for site_name in local_site_list - project_site_list:
      change = Change( type='site', action='local_delete', target_id=site_name )
      change.full_clean()
      change.save()
      have_changes = True

    if have_changes:
      return 'Local Site Changes'

    remote_site_list = set( contractor.getSiteList() )

    for site_name in local_site_list - remote_site_list:
      project_site = project[ site_name ]
      change = Change( type='site', action='remote_create', target_id=site_name, target_val={ 'description': project_site[ 'description' ], 'config_values': project_site[ 'config_values' ] } )
      change.full_clean()
      change.save()
      have_changes = True

    for site_name in remote_site_list - local_site_list:
      change = Change( type='site', action='remote_delete', target_id=site_name )
      change.full_clean()
      change.save()
      have_changes = True

    if have_changes:
      return 'Remote Site Changes'

    dirty = False
    for site_name in project_site_list:
      site = Site.objects.get( name=site_name )

      hasher = hashlib.sha1()
      hasher.update( str( project[ site_name ] ).encode() )
      current_hash = hasher.hexdigest()
      if site.last_load_hash == current_hash:
        continue

      site_dirty = False

      # first compare site values
      project_site = project[ site_name ]
      remote_site = contractor.getSite( site_name )

      print( '***' )
      pprint( site )
      print( '----' )
      pprint( project_site )
      print( '===' )

      # update site details
      change_list = _compare( remote_site, project_site, ( 'description', 'config_values' ) )
      if change_list:
        change = Change( type='site', action='change', target_id=site_name, current_val=dict( [ ( i, remote_site[ i ] ) for i in change_list ] ), target_val=dict( [ ( i, project_site[ i ] ) for i in change_list ] ) )
        change.full_clean()
        change.save()
        site_dirty = True

      # second check address_blocks
      project_address_block_list = set( project_site[ 'address_block' ].keys() )
      if not site_dirty:
        # create/destroy the address blocks
        remote_address_block_map = contractor.getAddressBlockMap( site_name )
        remote_address_block_list = set( remote_address_block_map.keys() )
        for block_name in project_address_block_list - remote_address_block_list:
          address_block = project_site[ 'address_block' ][ block_name ]
          change = Change( type='address_block', action='remote_create', site=site, target_id=block_name, target_val=address_block )
          change.full_clean()
          change.save()
          site_dirty = True

        for block_name in remote_address_block_list - project_address_block_list:
          address_block = project_site[ 'address_block' ][ block_name ]
          change = Change( type='address_block', action='remote_delete', site=site, target_id=block_name )
          change.full_clean()
          change.save()
          site_dirty = True

      if not site_dirty:
        # update address block details
        for block_name, remote_address_block in remote_address_block_map.items():
          project_address_block = project_site[ 'address_block' ][ block_name ]
          change_list = _compare( remote_address_block, project_address_block, ( 'subnet', 'prefix', 'gateway_offset', 'reserved_offset_list', 'dynamic_offset_list' ) )

          if change_list:
            change = Change( type='address_block', action='change', site=site, target_id=block_name,
                             current_val=dict( [ ( i, list( remote_address_block[ i ] ) ) for i in change_list ] ),
                             target_val=dict( [ ( i, project_address_block[ i ] ) for i in change_list ] ) )
            change.full_clean()
            change.save()
            site_dirty = True

      # third check instances
      project_instance_list = set( project_site[ 'instance' ].keys() )
      if not site_dirty:
        # create/destroy instances
        remote_instance_map = contractor.getInstanceMap( site_name )
        remote_instance_list = set( remote_instance_map.keys() )

        for instance_name in project_instance_list - remote_instance_list:
          instance = project_site[ 'instance' ][ instance_name ]
          change = Change( type='instance', action='remote_create', site=site, target_id=instance_name, target_val=instance )
          change.full_clean()
          change.save()
          site_dirty = True

        for instance_name in remote_instance_list - project_instance_list:
          instance = project_site[ 'instance' ][ instance_name ]
          change = Change( type='instance', action='remote_delete', site=site, target_id=instance_name )
          change.full_clean()
          change.save()
          site_dirty = True

      if not site_dirty:
        # update instance details
        for instance_name, remote_instance in remote_instance_map.items():
          project_instance = project_site[ 'instance' ][ instance_name ]
          change_list = _compare( remote_instance, project_instance, ( 'blueprint', 'type', 'address_list' ) )

          if change_list:
            change = Change( type='instance', action='change', site=site, target_id=instance_name,
                             current_val=dict( [ ( i, remote_instance[ i ] ) for i in change_list ] ),
                             target_val=dict( [ ( i, project_instance[ i ] ) for i in change_list ] ) )
            change.full_clean()
            change.save()
            site_dirty = True

      if site_dirty:
        dirty = True

      else:
        site.last_load = datetime.now( timezone.utc )
        site.last_load_hash = current_hash
        site.full_clean()
        site.save()

    if dirty:
      return 'Changes'
    else:
      return 'No Change'

    # clear Change table
    # load with the new changes

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True


@cinp.model( not_allowed_verb_list=[ 'DELETE', 'CREATE', 'UPDATE' ] )
class Change( models.Model ):
  type = models.CharField( max_length=13, choices=zip( CHANGE_TYPE_CHOICES, CHANGE_TYPE_CHOICES ) )
  action = models.CharField( max_length=13, choices=zip( CHANGE_ACTION_CHOICES, CHANGE_ACTION_CHOICES ) )
  site = models.ForeignKey( Site, blank=True, null=True, related_name='+' )
  target_id = models.CharField( max_length=50 )
  current_val = JSONField( blank=True, null=True )
  target_val = JSONField( blank=True, null=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @cinp.action( return_type='String' )
  def apply( self ):
    result = None

    if self.type == 'site':
      if self.action == 'local_create':
        site = Site( name=self.target_id )
        site.last_load = datetime.now( timezone.utc )
        site.last_load_hash = 'new'
        site.full_clean()
        site.save()

        result = 'Site "{0}" added locally'.format( self.target_id )

      elif self.action == 'remote_create':
        contractor = getContractor()
        contractor.createSite( self.target_id, **self.target_val )

        result = 'Site "{0}" added remotely'.format( self.target_id )

      elif self.action == 'change':
        contractor = getContractor()
        contractor.updateSite( self.target_id, **self.target_val )

        result = 'Site "{0}" updated fields: "{1}"'.format( self.target_id, '", "'.join( self.target_val.keys() ) )

      else:
        raise ValueError( 'Unknown Action "{0}" for site'.format( self.action ) )

    elif self.type == 'address_block':
      if self.action == 'remote_create':
        contractor = getContractor()
        contractor.createAddressBlock( self.site.name, self.target_id, **self.target_val )

        result = 'Address Block "{0}" added remotely'.format( self.target_id )

      elif self.action == 'change':
        contractor = getContractor()
        contractor.updateAddressBlock( self.target_id, **self.target_val )

        result = 'Address Block "{0}" updated fields: "{1}"'.format( self.target_id, '", "'.join( self.target_val.keys() ) )

      else:
        raise ValueError( 'Unknown Action "{0}" for address_block'.format( self.action ) )

    elif self.type == 'instance':
      if self.action == 'remote_create':
        contractor = getContractor()
        contractor.createInstance( self.site.name, self.target_id, **self.target_val )

        result = 'Instance "{0}" added remotely'.format( self.target_id )

      elif self.action == 'change':
        contractor = getContractor()
        contractor.updateInstance( self.target_id, **self.target_val )

        result = 'Instance "{0}" updated fields: "{1}"'.format( self.target_id, '", "'.join( self.target_val.keys() ) )

      else:
        raise ValueError( 'Unknown Action "{0}" for instance'.format( self.action ) )

    else:
      raise ValueError( 'Unknown Action "{0}"'.format( self.type ) )

    self.delete()
    return result

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.type != 'site' and self.site is None:
      errors[ 'site' ] = 'Required when type is not "site"'

    if self.target_val is None and self.action not in ( 'local_create', 'remote_create', 'local_delete', 'remote_delete' ):
      errors[ 'target_val' ] = 'Required when not Creating'

    if self.current_val is None and self.action not in ( 'local_create', 'remote_create', 'local_delete', 'remote_delete' ):
      errors[ 'current_val' ] = 'Required when not Deleteing'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True
