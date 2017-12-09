import string
import random

from django.db import models

from cinp.orm_django import DjangoCInP as CInP
from django.core.exceptions import ValidationError

from datetime import datetime, timezone

from architect.Contractor.models import Complex, BluePrint
from architect.Plan.models import Plan

from architect.Contractor.libcontractor import getContractor

cinp = CInP( 'Builder', '0.1' )


@cinp.model( property_list=[ 'state', 'config_values' ], not_allowed_method_list=[ 'DELETE', 'CREATE', 'CALL', 'UPDATE' ] )
class Instance( models.Model ):
  nonce = models.CharField( max_length=26, unique=True )
  plan = models.ForeignKey( Plan, on_delete=models.PROTECT )
  complex = models.ForeignKey( Complex, on_delete=models.PROTECT )
  blueprint = models.ForeignKey( BluePrint, on_delete=models.PROTECT )
  hostname = models.CharField( max_length=200, unique=True )
  contractor_id = models.IntegerField( null=True, blank=True, unique=True )  # Contractor structure id
  requested_at = models.DateTimeField( null=True, blank=True )
  built_at = models.DateTimeField( null=True, blank=True )
  unrequested_at = models.DateTimeField( null=True, blank=True )
  destroyed_at = models.DateTimeField( null=True, blank=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def setRequested( self ):
    self.requested_at = datetime.now( timezone.utc )
    self.built_at = None
    self.unrequested_at = None
    self.destroyed_at = None
    self.full_clean()
    self.save()

  def setBuilt( self ):
    if self.requested_at is None:
      self.requested_at = datetime.now( timezone.utc )
    self.built_at = datetime.now( timezone.utc )
    self.unrequested_at = None
    self.destroyed_at = None
    self.full_clean()
    self.save()

  def setUnrequested( self ):
    if self.requested_at is None:
      self.requested_at = datetime.now( timezone.utc )
    if self.built_at is None:
      self.built_at = datetime.now( timezone.utc )
    self.unrequested_at = datetime.now( timezone.utc )
    self.destroyed_at = None
    self.full_clean()
    self.save()

  def setDestroyed( self ):
    if self.requested_at is None:
      self.requested_at = datetime.now( timezone.utc )
    if self.built_at is None:
      self.built_at = datetime.now( timezone.utc )
    if self.unrequested_at is None:
      self.unrequested_at = datetime.now( timezone.utc )
    self.destroyed_at = datetime.now( timezone.utc )
    self.full_clean()
    self.save()

  @staticmethod
  def create( plan, complex_tsname, blueprint_name ):
    result = Instance( plan=plan, complex=Complex.objects.get( tsname=complex_tsname ), blueprint=BluePrint.objects.get( name=blueprint_name ) )
    result.nonce = plan.nextNonce()
    result.hostname = plan.hostname_pattern.format( **{ 'plan': plan.name, 'compex': complex_tsname, 'blueprint': blueprint_name, 'site': result.complex.site_id, 'nonce': result.nonce } )
    result.requested_at = datetime.now( timezone.utc )
    result.full_clean()
    result.save()
    return result

  @property
  def state( self ):  # TODO: more status for rebuilding and moving?
    if not self.destroyed_at and not self.unrequested_at and not self.built_at and not self.requested_at:
      return 'new'

    if not self.destroyed_at and not self.unrequested_at and not self.built_at and self.requested_at:
      return 'requested'

    if not self.destroyed_at and not self.unrequested_at and self.built_at:
      return 'built'

    if not self.destroyed_at and self.unrequested_at:
      return 'removing'

    if self.destroyed_at:
      return 'destroyed'

    return 'unknown'

  @property
  def config_values( self ):
    result = self.plan.config_values

    return result

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not self.contractor_id:
      self.contractor_id = None

    errors = {}

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Instance({0}) "{1}" of "{2}" in "{3}" blueprint "{4}"'.format( self.pk, self.hostname, self.plan.name, self.complex, self.blueprint )


@cinp.model( not_allowed_method_list=[ 'DELETE', 'CREATE', 'UPDATE' ] )
class Job( models.Model ):
  JOB_ACTION_CHOICES = ( ( 'build', 'build' ), ( 'destroy', 'destroy' ), ( 'rebuild', 'rebuild' ), ( 'move', 'move' ) )
  JOB_STATE_CHOICES = ( ( 'new', 'new' ), ( 'waiting', 'waiting' ), ( 'done', 'done' ), (  'error', 'error' ) )
  instance = models.OneToOneField( Instance, on_delete=models.CASCADE )
  action = models.CharField( max_length=7, choices=JOB_ACTION_CHOICES )
  state = models.CharField( max_length=7, choices=JOB_STATE_CHOICES )
  web_hook_token = models.CharField( max_length=30, blank=True, null=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @staticmethod
  def create( instance, action ):
    job = Job( instance=instance, action=action )
    job.state = 'new'
    job.full_clean()
    job.save()
    return job

  def _registerWebHook( self, contractor ):
    self.web_hook_token = ''.join( random.choice( string.ascii_letters ) for _ in range( 30 ) )
    self.state = 'waiting'
    self.full_clean()
    contractor.registerWebHook( self.pk, self.instance.contractor_id, self.web_hook_token )
    self.save()

  def run( self ):
    if self.state == 'done':
      if self.action == 'build':
        self.instance.setBuilt()

      elif self.action == 'destroy':
        self.instance.setDestroyed()

      elif self.action == 'rebuild':
        self.instance.setDestroyed()
        Job.create( self.instance, 'build' )

      self.delete()

    if self.state == 'new':
      contractor = getContractor()
      if self.action == 'build':
        if self.instance.contractor_id is None:
          structure = contractor.createStructure( self.instance.complex.contractor_id, self.instance.blueprint.contractor_id, self.instance.hostname )
          self.instance.contractor_id = structure
          self.instance.save()
          self.instance.full_clean()

        self._registerWebHook( contractor )
        self.instance.setRequested()

      elif self.action == 'destroy':
        contractor.destroyStructure( self.instance.contractor_id, delete=True )
        self._registerWebHook( contractor )
        self.instance.setUnrequested()

      elif self.action == 'rebuild':
        contractor.destroyStructure( self.instance.contractor_id )
        self._registerWebHook( contractor )
        self.instance.setUnrequested()

      else:
        raise Exception( 'Not implemented' )

    # ignore every other state

  @cinp.action( return_type='String', paramater_type_list=[ 'String', 'String', 'String', 'String' ] )
  def jobNotify( self, token, structure, script, at ):
    if token != self.web_hook_token:
      return 'invalid token'

    self.web_hook_token = None
    self.state = 'done'
    self.full_clean()
    self.save()

    return 'thanks'

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Job({0}) for {1}'.format( self.pk, self.instance )
