import re

from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from architect.Contractor.models import Complex
from architect.TimeSeries.libts import getTS

LAST_VALUE_MAX_AGE = 3600  # in seconds

SCALER_CHOICES = ( ( 'none', 'None' ), ( 'step', 'Step' ), ( 'linear', 'Linear' ) )
metric_regex = re.compile( '^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*$' )
member_name_regex = re.compile( '^[a-zA-Z0-9\-_]{2,50}$' )

cinp = CInP( 'TimeSeries', '0.1' )


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class TimeSeries( models.Model ):
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return ''

  @property
  def last_value( self ):
    return None

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  class Meta:
    abstract = True


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class RawTimeSeries( TimeSeries ):
  metric = models.CharField( max_length=200 )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return getTS().graph( self.metric, start_offset, end_offset, height, width )

  @property
  def last_value( self ):
    return getTS().get_last( self.metric, LAST_VALUE_MAX_AGE )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not metric_regex.match( self.metric ):
      raise ValidationError( 'Metric "{0}" is invalid'.format( self.name ) )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class CostTS( TimeSeries ):
  complex = models.OneToOneField( Complex, on_delete=models.CASCADE )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return getTS().graph( 'complex.{0}.cost'.format( self.complex.tsname ), start_offset, end_offset, height, width )

  @property
  def last_value( self ):
    return getTS().get_last( 'complex.{0}.cost'.format( self.complex.tsname ), LAST_VALUE_MAX_AGE )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if self.complex.tsname is None:
      errors[ 'complex' ] = 'can not use a complex without a tsname set.'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class AvailabilityTS( TimeSeries ):
  complex = models.OneToOneField( Complex, on_delete=models.CASCADE )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return getTS().graph( 'complex.{0}.availability'.format( self.complex.tsname ), start_offset, end_offset, height, width )

  @property
  def last_value( self ):
    return getTS().get_last( 'complex.{0}.availability'.format( self.complex.tsname ), LAST_VALUE_MAX_AGE )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class ReliabilityTS( TimeSeries ):
  complex = models.OneToOneField( Complex, on_delete=models.CASCADE )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return getTS().graph( 'complex.{0}.reliability'.format( self.complex.tsname ), start_offset, end_offset, height, width )

  @property
  def last_value( self ):
    return getTS().get_last( 'complex.{0}.reliability'.format( self.complex.tsname ), LAST_VALUE_MAX_AGE )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True


@cinp.model( property_list=[ 'uid' ], not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class Controller( models.Model ):  # this fields should match the default member in lib.py
  """
min/max_instance -> control the limits
query -> query to get from data source
lockout_query -> if this query returns != 0, no adjustment  is allowed
a_value, b_value -> for value prediction. None -> no prediction, ie t+1 = t
p_value -> for linter
step_threshold -> for step mode
deadband_with ->
cooldown_seconds -> delay after change before allowing more, to keep thing from  overreacting
can_grow -> allowed to grow
can_shrink -> allowed to shrink
  """
  name = models.CharField( max_length=50, primary_key=True )
  # inspector data - type,p,metric,lockout_metric
  # safety_data - heart beat interval, health check
  # security_data - required ports
  scaler_type = models.CharField( max_length=5, choices=SCALER_CHOICES, default='none' )
  min_instances = models.IntegerField( null=True, blank=True )
  max_instances = models.IntegerField( null=True, blank=True )
  build_ahead = models.IntegerField( default=0 )
  regenerate_rate = models.IntegerField( default=1 )
  tsd_metric = models.CharField( max_length=200, null=True, blank=True )
  lockout_query = models.CharField( max_length=200, null=True, blank=True )
  p_value = models.FloatField( null=True, blank=True )
  a_value = models.FloatField( null=True, blank=True )
  b_value = models.FloatField( null=True, blank=True )
  step_threshold = models.FloatField( null=True, blank=True )
  deadband_margin = models.IntegerField( null=True, blank=True )
  cooldown_seconds = models.IntegerField( default=60 )
  can_grow = models.BooleanField( default=False )
  can_shrink = models.BooleanField( default=False )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @property
  def active_count( self ):
    return self.instance_set.filter( provisioned_at__isnull=False, unrequested_at__isnull=True ).count()

  @property
  def provisioning_count( self ):
    return self.instance_set.filter( requested_at__isnull=False, provisioned_at__isnull=True ).count()

  @property
  def deprovisioining_count( self ):
    return self.instance_set.filter( provisioned_at_isnull=False, deprovisioned_at__isnull=True ).count()

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )

    if self.tsd_metric == '':
      self.tsd_metric = None

    if self.lockout_query == '':
      self.lockout_query = None

    errors = {}

    if not member_name_regex.match( self.name ):
      errors[ 'name' ] = 'Invalid "{0}"'.format( self.name )

    if self.scaler_type != 'none' and self.tsd_metric is None:
      errors[ 'tsd_metric' ] = 'tsd_metric is required if scaler_type is not None'

    if self.tsd_metric is not None:
      if self.a_value is None:
        errors[ 'a_value' ] = 'required when there is a metric'

      if self.b_value is None:
        errors[ 'b_value' ] = 'required when there is a metric'

      if self.deadband_margin is None:
        errors[ 'deadband_margin' ] = 'required when there is a metric'

    if self.scaler_type == 'linear':
      if self.p_value is None:
        errors[ 'p_value' ] = 'required for scaler_type "linear"'

      elif self.p_value == 0:
        errors[ 'p_value' ] = 'can not be 0 for scaler_type "linear"'

      if ( self.a_value + self.b_value ) > 1:
        errors[ 'a_value' ] = 'a_value + b_value can not exceed 1'

    if self.scaler_type == 'step':
      if self.step_threshold is None:
        errors[ 'step_threshold' ] = 'required for scaler_type "step"'

      elif self.step_threshold == 0:
        errors[ 'step_threshold' ] = 'can not be 0 for scaler_type "step"'

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Controller "{0}"'.format( self.name )
