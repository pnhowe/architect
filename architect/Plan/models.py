import hashlib
import base64

from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from architect.TimeSeries.models import CostTS, AvailabilityTS, ReliabilityTS, RawTimeSeries
from architect.Contractor.models import Complex, BluePrint
from architect.fields import MapField, script_name_regex
from architect.tcalc.parser import lint


cinp = CInP( 'Plan', '0.1' )


@cinp.model( not_allowed_method_list=[ 'CALL' ] )
class Plan( models.Model ):
  """
  hostname_pattern -> python.format format,
                       {plan} -> plan name (up to 50 chars)
                       {compex} -> complex name (up to 50 chars)
                       {blueprint} -> blueprint name (up to 50 chars)
                       {site} -> site name (up to 40 chars)
                       {nonce} -> nonce (random one-time use string, 26 chars)
    the target hostname is length 200 chars
  """
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
  enabled = models.BooleanField( default=False )  # enabled to be scanned and updated that is, any existing resources will not be affected
  hostname_pattern = models.CharField( max_length=100, default='{plan}-{nonce}' )
  config_values = MapField( blank=True )
  script = models.TextField()  # TODO: on save run lint
  complex_list = models.ManyToManyField( Complex, through='PlanComplex' )
  blueprint_list = models.ManyToManyField( BluePrint, through='PlanBluePrint' )
  timeseries_list = models.ManyToManyField( RawTimeSeries, through='PlanTimeSeries' )
  static_values = models.TextField( blank=True, null=True )
  slots_per_complex = models.IntegerField( default=100 )
  change_cooldown = models.IntegerField( default=300 )  # in seconds
  max_inflight = models.IntegerField( default=2 )  # number of things that can be changing at the same time
  last_change = models.DateTimeField()
  nonce_counter = models.IntegerField( default=1 )  # is hashed (with other stuff) to be used as the nonc string, https://stackoverflow.com/questions/4567089/hash-function-that-produces-short-hashes
  can_move = models.BooleanField( default=False )
  can_destroy = models.BooleanField( default=False )
  can_build = models.BooleanField( default=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def nextNonce( self ):
    plan = Plan.objects.select_for_update().get( name=self.name )
    counter = plan.nonce_counter
    plan.nonce_counter += 1
    plan.save()

    # nonce must be hostname safe and lowercase
    nonce = hashlib.md5()
    nonce.update( '{0:20d}'.format( counter ).encode() )
    nonce.update( self.name.encode() )

    return base64.b32encode( nonce.digest() ).strip( b'=' ).lower().decode()

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.slots_per_complex < 1 or self.slots_per_complex > 5000:
      errors[ 'slots_per_complex' ] = 'must be from 1 to 5000'

    result = lint( self.script )
    if result is not None:
      errors[ 'script' ] = result

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Plan "{0}"'.format( self.name )


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class PlanComplex( models.Model ):
  plan = models.ForeignKey( Plan, on_delete=models.CASCADE )
  complex = models.ForeignKey( Complex, on_delete=models.PROTECT )  # deleting this will cause the indexing to get messed up, have to deal with that before deleting
  cost = models.ForeignKey( CostTS, related_name='+', on_delete=models.PROTECT )  # 0 -> large value
  availability = models.ForeignKey( AvailabilityTS, related_name='+', on_delete=models.PROTECT )  # 0.0 -> 1.0
  reliability = models.ForeignKey( ReliabilityTS, related_name='+', on_delete=models.PROTECT )  # 0.0 -> 1.0
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'PlanComplex for Plan "{0}" to "{1}"'.format( self.plan, self.complex )

  class Meta:
    unique_together = ( ( 'plan', 'complex' ), )


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class PlanBluePrint( models.Model ):
  plan = models.ForeignKey( Plan, on_delete=models.CASCADE  )
  blueprint = models.ForeignKey( BluePrint, on_delete=models.PROTECT  )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.blueprint.name is None:
      errors[ 'blueprint' ] = 'Blueprint must have an assigned name'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'PlanBluePrint for Plan "{0}" to "{1}" '.format( self.plan, self.blueprint.name )

  class Meta:
    unique_together = ( ( 'plan', 'blueprint' ), )


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class PlanTimeSeries( models.Model ):
  plan = models.ForeignKey( Plan, on_delete=models.CASCADE  )
  timeseries = models.ForeignKey( RawTimeSeries, related_name='+', on_delete=models.PROTECT   )
  script_name = models.CharField( max_length=50 )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not script_name_regex.match( self.script_name ):
      errors[ 'script_name' ] = '"{0}" is invalid'.format( self.script_name )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'PlanTimeSeries for Plan "{0}" to "{1}" with name "{2}"'.format( self.plan, self.timeseries, self.script_name )

  class Meta:
    unique_together = ( ( 'plan', 'timeseries' ), )
