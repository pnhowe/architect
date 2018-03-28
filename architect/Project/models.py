import os

from django.db import models
from django.conf import settings

from cinp.orm_django import DjangoCInP as CInP
from django.core.exceptions import ValidationError

from architect.Plan.models import Site
from architect.fields import JSONField

from architect.Contractor.libcontractor import getContractor

from architect.Project.load import loadProject, validateProject
from architect.Project.compare import ProjectComparer
from architect.Project.apply import applyChange


cinp = CInP( 'Project', '0.1', doc="""This is the loader for the Project as a whole
""" )

CHANGE_TYPE_CHOICES = ( 'site', 'address_block', 'structure' )
CHANGE_ACTION_CHOICES = ( 'local_create', 'remote_create', 'local_delete', 'remote_delete', 'change' )


@cinp.model( not_allowed_verb_list=[ 'DELETE', 'CREATE', 'UPDATE', 'LIST', 'GET' ] )
class Loader( models.Model ):

  @cinp.action( return_type='String' )
  @staticmethod
  def rescan():
    if not os.path.isfile( os.path.join( settings.PROJECT_PATH, 'architect.toml' ) ):
      return 'Unable to find project file'

    project = loadProject( settings.PROJECT_PATH )

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
    result = applyChange( self )

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
