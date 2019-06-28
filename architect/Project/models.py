import os
from datetime import datetime, timezone

from django.db import models
from django.conf import settings

from cinp.orm_django import DjangoCInP as CInP
from django.core.exceptions import ValidationError

from architect.fields import MapField, JSONField, plan_name_regex

from architect.Contractor.Contractor import getContractor

from architect.Project.git import Git
from architect.Project.load import loadProject, validateProject
from architect.Project.compare import ProjectComparer
from architect.Project.apply import applyChange


cinp = CInP( 'Project', '0.1', doc="""This is the loader for the Project as a whole
""" )

CHANGE_TYPE_CHOICES = ( 'site', 'address_block', 'structure', 'complex', 'plan' )
CHANGE_ACTION_CHOICES = ( 'local_create', 'remote_create', 'local_delete', 'remote_delete', 'change' )


def getGit():
  return Git( settings.GIT_URL, settings.GIT_BRANCH, settings.PROJECT_WORK_PATH )


@cinp.model( not_allowed_verb_list=[ 'CALL' ], read_only_list=[ 'last_change' ] )
class Site( models.Model ):
  name = models.CharField( max_length=50, primary_key=True )  # also the id on Contractor
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.CASCADE )
  static_entry_map = MapField( blank=True )
  address_block_map = MapField( blank=True )

  last_load_hash = models.CharField( max_length=40 )  # sha1
  last_load = models.DateTimeField()

  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if not plan_name_regex.match( self.name ):
      errors[ 'name' ] = '"{0}" is invalid'.format( self.name )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Site "{0}"'.format( self.name )


@cinp.model( not_allowed_verb_list=[ 'DELETE', 'CREATE', 'UPDATE' ] )
class Loader( models.Model ):
  current_hash = models.CharField( max_length=40 )
  last_update = models.DateTimeField()
  upstream_hash = models.CharField( max_length=40 )
  last_check = models.DateTimeField()
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @cinp.action()
  @staticmethod
  def update():
    git = getGit()
    if not os.path.exists( settings.PROJECT_WORK_PATH ):
      git.checkout()

    git.update()

    rec = Loader.objects.get()
    rec.current_hash = git.local_hash()
    rec.last_update = datetime.now( timezone.utc )
    rec.full_clean()
    rec.save()

  @cinp.action()
  @staticmethod
  def check_upstream():
    git = getGit()

    rec = Loader.objects.get()
    rec.upstream_hash = git.remote_hash()
    rec.last_check = datetime.now( timezone.utc )
    rec.full_clean()
    rec.save()

  @cinp.action( return_type='String' )
  @staticmethod
  def rescan():
    if not os.path.isfile( os.path.join( settings.PROJECT_WORK_PATH, 'architect.toml' ) ):
      return 'Unable to find project file'

    project = loadProject( settings.PROJECT_WORK_PATH )

    try:
      validateProject( project )
    except ValueError as e:
      return 'Error Validating Project: "{0}"'.format( e )

    Change.objects.all().delete()

    comparer = ProjectComparer( project, getContractor() )

    if not comparer.compare():
      return 'No Change'

    for change in comparer.change:
      change = Change( **change )
      change.full_clean()
      change.save()

    return comparer.message

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.pk != 1:
      errors[ 'pk' ] = 'Must be 1, only one reccord allowed'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, verb, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Loader Status'


@cinp.model( not_allowed_verb_list=[ 'DELETE', 'CREATE', 'UPDATE' ] )
class Change( models.Model ):
  type = models.CharField( max_length=13, choices=zip( CHANGE_TYPE_CHOICES, CHANGE_TYPE_CHOICES ) )
  action = models.CharField( max_length=13, choices=zip( CHANGE_ACTION_CHOICES, CHANGE_ACTION_CHOICES ) )
  site = models.ForeignKey( Site, blank=True, null=True, related_name='+', on_delete=models.PROTECT )
  target_id = models.CharField( max_length=50 )
  current_val = JSONField( blank=True, null=True )
  target_val = JSONField( blank=True, null=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @cinp.action( return_type='Map' )
  def apply( self ):
    if self.id > Change.objects.all().order_by( 'pk' )[0].id:
      raise ValueError( 'Can only apply the first change' )

    result = applyChange( self )

    self.delete()
    return { 'result': result }

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}

    if self.site is None and self.type not in ( 'site', 'plan' ):
      errors[ 'site' ] = 'Required when type is not "site" or "plan"'

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

  class Meta:
    ordering = [ 'pk' ]
