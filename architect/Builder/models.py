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
  def state( self ):
    if self.contractor_id is None:
      return 'planned'

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
    return 'Instance "{0}" of "{1}" in "{2}" blueprint "{3}"'.format( self.hostname, self.plan.name, self.complex, self.blueprint )


@cinp.model( not_allowed_method_list=[ 'DELETE', 'CREATE', 'CALL', 'UPDATE' ] )
class Job( models.Model ):
  JOB_ACTION_CHOICES = ( ( 'build', 'build' ), ( 'destroy', 'destroy' ), ( 'rebuild', 'rebuild' ), ( 'move', 'move' ) )
  instance = models.OneToOneField( Instance, on_delete=models.CASCADE )
  action = models.CharField( max_length=7, choices=JOB_ACTION_CHOICES )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @staticmethod
  def create( instance, action ):
    contractor = getContractor()
    if action == 'build':
      if instance.contractor_id is None:
        structure = contractor.createStructure( instance.complex.contractor_id, instance.blueprint.contractor_id, instance.hostname )
        instance.contractor_id = structure
        instance.full_clean()
        instance.save()

        # register webhook so we know when it is done

    else:
      raise Exception( 'Not implemented' )

  def jobFinished( self ):
    if self.action == 'build':
      self.instance.setBuilt()

    elif self.action == 'destroy':
      self.instance.setDestroyed()

    elif self.action == 'rebuild':
      self.instance.setDestroyed()
      Job.create( self.instance, 'build' )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Job id "{0}" for {1}'.format( self.id, self.instance )
