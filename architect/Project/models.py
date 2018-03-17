import os
import hashlib
from datetime import datetime, timezone

from pprint import pprint

from django.db import models
from django.conf import settings

from cinp.orm_django import DjangoCInP as CInP
from cinp.client import NotFound
from django.core.exceptions import ValidationError

from architect.Plan.models import Site
from architect.fields import JSONField

from architect.Project.lib import loadProject, validateProject
from architect.Contractor.libcontractor import getContractor

cinp = CInP( 'Project', '0.1', doc="""This is the loader for the Project as a whole
""" )

CHANGE_TYPE_CHOICES = ( 'site', 'address_block' )
CHANGE_ACTION_CHOICES = ( 'local_create', 'remote_create', 'local_delete', 'remote_delete', 'change' )


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

    site_list = set( Site.objects.all().values_list( 'name', flat=True ) )
    target_site_list = set( project.keys() )

    have_changes = False

    for name in target_site_list - site_list:
      change = Change( type='site', action='local_create', target_id=name )
      change.full_clean()
      change.save()
      have_changes = True

    for name in site_list - target_site_list:
      change = Change( type='site', action='local_delete', target_id=name )
      change.full_clean()
      change.save()
      have_changes = True

    if have_changes:
      return 'Local Site Changes'

    remote_site_list = set( contractor.getSiteList() )

    for name in site_list - remote_site_list:
      change = Change( type='site', action='remote_create', target_id=name, target_val={ 'description': project[ name ][ 'description' ] } )
      change.full_clean()
      change.save()
      have_changes = True

    for name in remote_site_list - site_list:
      change = Change( type='site', action='remote_delete', target_id=name )
      change.full_clean()
      change.save()
      have_changes = True

    if have_changes:
      return 'Remote Site Changes'

    for name in site_list:
      site = Site.objects.get( name=name )

      hasher = hashlib.sha1()
      hasher.update( str( project[ name ] ).encode() )
      current_hash = hasher.hexdigest()
      if site.last_load_hash == current_hash:
        continue

      dirty = False

      # first compare site values
      csite = contractor.getSite( name )
      psite = project[ name ]
      pprint( csite )
      pprint( site )
      pprint( psite )

      change_list = []
      for i in ( 'description', 'config_values', ):
        if csite[ i ] != psite[ i ]:
          change_list.append( i )

      if change_list:
        change = Change( type='site', action='change', target_id=name, current_val=dict( [ ( i, csite[ i ] ) for i in change_list ] ), target_val=dict( [ ( i, psite[ i ] ) for i in change_list ] ) )
        change.full_clean()
        change.save()
        dirty = True

      # second check address_blocks
      # get from Contractor
      address_block_list = set( AddressBlock.object.filter( site=site ).values_list( 'name', flat=True ) )
      target_address_block_list = set( project[ site ][ 'address_block' ].keys() )
      for name in target_address_block_list - address_block_list:  # TODO deal with removed address_blocks
        address_block = project[ site ][ 'address_block' ][ name ]
        change = Change( type='address_block', action='create', site=site, current_val=None, target_val=address_block )
        change.full_clean()
        change.save()
        dirty = True

      # for name in project[ site ][ 'address_block' ]:
      #   address_block = project[ site ][ 'address_block' ][ name ]

      # update site with the results
      if dirty:
        have_changes = True

      else:
        site.last_load = datetime.now( timezone.utc )
        site.last_load_hash = current_hash
        site.full_clean()
        site.save()

    if have_changes:
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
  type = models.CharField( max_length=10, choices=zip( CHANGE_TYPE_CHOICES, CHANGE_TYPE_CHOICES ) )
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
        contractor.createSite( self.target_id, self.target_val[ 'description' ] )

        result = 'Site "{0}" added remotely'.format( self.target_id )

      elif self.action == 'change':
        contractor = getContractor()
        contractor.updateSite( self.target_id, **self.target_val )

        result = 'Site "{0}" updated fields: "{1}"'.format( self.target_id, '", "'.join( self.target_val.keys() ) )

      else:
        raise ValueError( 'Unknown Action "{0}"'.format( self.action ) )

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
