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


@cinp.model( not_allowed_method_list=[ 'DELETE', 'CREATE', 'CALL', 'UPDATE' ] )
class Instance( models.Model ):
  nonce = models.CharField( max_length=26, unique=True )
  plan = models.ForeignKey( Plan, on_delete=models.PROTECT )
  complex = models.ForeignKey( Complex, on_delete=models.PROTECT )
  blueprint = models.ForeignKey( BluePrint, on_delete=models.PROTECT )
  hostname = models.CharField( max_length=200, unique=True )
  foundation_id = models.IntegerField( null=True, blank=True, unique=True )  # Contractor foundation id
  structure_id = models.IntegerField( null=True, blank=True, unique=True )  # Contractor structure id
  foundation_built = models.BooleanField( default=False )
  structure_built = models.BooleanField( default=False )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def destroy( self ):
    self.setUnrequested()

  @staticmethod
  def create( plan, complex_tsname, blueprint_name ):
    result = Instance( plan=plan, complex=Complex.objects.get( tsname=complex_tsname ), blueprint=BluePrint.objects.get( name=blueprint_name ) )
    result.nonce = plan.nextNonce()
    result.hostname = plan.hostname_pattern.format( **{ 'plan': plan.name, 'compex': complex_tsname, 'blueprint': blueprint_name, 'site': result.complex.site_id, 'nonce': result.nonce } )
    result.full_clean()
    result.save()
    return result

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not self.foundation_id:
      self.foundation_id = None

    if not self.structure_id:
      self.structure_id = None

    errors = {}

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Instance({0}) "{1}" of "{2}" in "{3}" blueprint "{4}"'.format( self.pk, self.hostname, self.plan.name, self.complex, self.blueprint )

# TODO: when issue #9 in cinp/python is resolved, move this into Job
# also use this for the lengths for the History Table, also get rid of the
# length constants
#  target = models.CharField( max_length=Job._meta.get_field( 'target' ).max_length, choices=Job.JOB_TARGET_CHOICES )
#  action = models.CharField( max_length=Job._meta.get_field( 'action' ).max_length, choices=Job.JOB_ACTION_CHOICES )
# and move History after Job
JOB_TARGET_LENGTH = 10
JOB_ACTION_LENGTH = 7
JOB_TARGET_CHOICES = ( ( 'foundation', 'foundation' ), ( 'structure', 'structure' ) )
JOB_ACTION_CHOICES = ( ( 'build', 'build' ), ( 'destroy', 'destroy' ), ( 'move', 'move' ) )
JOB_STATE_CHOICES = ( ( 'new', 'new' ), ( 'waiting', 'waiting' ), ( 'done', 'done' ), ( 'error', 'error' ) )


@cinp.model( not_allowed_method_list=[ 'DELETE', 'CREATE', 'UPDATE' ] )
class History( models.Model ):
  instance = models.ForeignKey( Instance, on_delete=models.CASCADE )
  target = models.CharField( max_length=JOB_TARGET_LENGTH, choices=JOB_TARGET_CHOICES )
  action = models.CharField( max_length=JOB_ACTION_LENGTH, choices=JOB_ACTION_CHOICES )
  started = models.DateTimeField()
  completed = models.DateTimeField( blank=True, null=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not self.completed:
      self.completed = None

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'History({0}) for "{1}({2})" doing "{3}" at "{4}"'.format( self.pk, self.instance, self.target, self.action, self.created )


@cinp.model( not_allowed_method_list=[ 'DELETE', 'CREATE', 'UPDATE' ] )
class Job( models.Model ):
  instance = models.OneToOneField( Instance, on_delete=models.CASCADE )
  history_entry = models.OneToOneField( History, on_delete=models.CASCADE )
  target = models.CharField( max_length=JOB_TARGET_LENGTH, choices=JOB_TARGET_CHOICES )
  action = models.CharField( max_length=JOB_ACTION_LENGTH, choices=JOB_ACTION_CHOICES )
  state = models.CharField( max_length=7, choices=JOB_STATE_CHOICES )
  web_hook_token = models.CharField( max_length=30, blank=True, null=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @staticmethod
  def create( instance, target, action ):
    entry = History( instance=instance, target=target, action=action, started=datetime.now( timezone.utc ) )
    entry.full_clean()
    entry.save()
    job = Job( instance=instance, target=target, action=action )
    job.history_entry = entry
    job.state = 'new'
    job.full_clean()
    job.save()
    return job

  def _registerWebHook( self, contractor ):
    self.web_hook_token = ''.join( random.choice( string.ascii_letters ) for _ in range( 30 ) )
    self.state = 'waiting'
    self.full_clean()
    contractor.registerWebHook( self.target, self.pk, ( self.instance.foundation_id if self.target == 'foundation' else self.instance.structure_id ), self.web_hook_token )
    self.save()

  def run( self ):
    if self.state == 'done':
      if self.action == 'build':
        if self.target == 'foundation':
          self.instance.foundation_built = True

        else:
          self.instance.structure_built = True

      elif self.action == 'destroy':
        if self.target == 'foundation':
          self.instance.foundation_built = False
          self.instance.foundation_id = None

        else:
          self.instance.structure_built = False
          self.instance.structure_id = None

      self.instance.full_clean()
      self.instance.save()
      self.history_entry.completed = datetime.now( timezone.utc )
      self.history_entry.full_clean()
      self.history_entry.save()
      self.delete()

    if self.state == 'new':
      contractor = getContractor()
      if self.action == 'build':
        if self.target == 'foundation':
          if self.instance.foundation_id is None:
            self.instance.foundation_id = contractor.createFoundation( self.instance.complex.contractor_id, self.instance.blueprint.contractor_id, self.instance.hostname )

          if self.instance.structure_id is None:
            self.instance.structure_id = contractor.createStructure( self.instance.complex.site_id, self.instance.foundation_id, self.instance.blueprint.contractor_id, self.instance.hostname, self.instance.plan.config_values )

          self.instance.save()
          self.instance.full_clean()
          contractor.buildFoundation( self.instance.foundation_id )

        else:
          contractor.buildStructure( self.instance.structure_id )

        self._registerWebHook( contractor )

      elif self.action == 'destroy':
        if self.target == 'foundation':
          contractor.destroyFoundation( self.instance.foundation_id )
        else:
          contractor.destroyStructure( self.instance.structure_id )

        self._registerWebHook( contractor )

      else:
        raise Exception( 'Not implemented' )

    # ignore every other state

  @cinp.action( return_type='String', paramater_type_list=[ 'String', 'String', 'String', 'String', 'Integer', 'Integer' ] )
  def jobNotify( self, token, target, script, at, foundation=None, structure=None ):
    if token != self.web_hook_token or target != self.target:
      return 'invalid token and/or target'

    if ( self.target == 'foundation' and foundation != self.instance.foundation_id ) or ( self.target == 'structure' and structure != self.instance.structure_id ):
      return 'invalid id'

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
