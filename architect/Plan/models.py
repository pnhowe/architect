import re

from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from architect.TimeSeries.models import CostTS, AvailabilityTS, ReliabilityTS, RawTimeSeries
from architect.Contractor.models import Complex, BluePrint
from architect.fields import MapField
from architect.tcalc.parser import lint

SCALER_CHOICES = ( ( 'none', 'None' ), ( 'step', 'Step' ), ( 'linear', 'Linear' ) )

site_name_regex = re.compile( '^[a-zA-Z0-9\-]{2,10}$' )
member_name_regex = re.compile( '^[a-zA-Z0-9\-_]{2,50}$' )
script_name_regex = re.compile( '^[a-zA-Z0-9][a-zA-Z0-9_\-]*$' )

cinp = CInP( 'Plan', '0.1' )


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class Plan( models.Model ):
  name = models.CharField( max_length=50, primary_key=True )
  description = models.CharField( max_length=200 )
  enabled = models.BooleanField( default=False )  # enabled to be scanned and updated that is, any existing resources will not be affected
  script = models.TextField()  # TODO: on save run lint
  complex_list = models.ManyToManyField( Complex, through='PlanComplex' )
  blueprint_list = models.ManyToManyField( BluePrint, through='PlanBluePrint' )
  timeseries_list = models.ManyToManyField( RawTimeSeries, through='PlanTimeSeries' )
  static_values = models.TextField( blank=True, null=True )
  slots_per_complex = models.IntegerField( default=100 )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

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
    return 'PlanBluePrint for Plan "{0}" to "{1}" with name "{2}"'.format( self.plan, self.blueprint, self.script_name )

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


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class Site( models.Model ):
  name = models.CharField( max_length=20, primary_key=True )  # same length as contractor.site.name
  description = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', null=True, blank=True, on_delete=models.PROTECT  )
  config_values = MapField( blank=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    errors = {}
    if not site_name_regex.match( self.name ):
      errors[ 'name' ] = '"{0}" is invalid'.format( self.name )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Site "{0}"({1})'.format( self.description, self.name )


@cinp.model( property_list=[ 'uid' ], not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class Member( models.Model ):  # this fields should match the default member in lib.py
  """
hostname_pattern -> python.format format, {offset} -> incramenting number for blueprint in site, {id} -> structure id, {blueprint} -> blueprint name, {site} -> site name
config_profile, config_priority, config_values, auto_configure -> values to configure plato with
deploy_to -> if there is a vmhost to deploy to
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
member_affinity -> positive - keep togeahter, negative keep apart. -10 -> 10 (-10 never put members on same host, 10 allways put members on same host)
  """
  site = models.ForeignKey( Site, editable=False, on_delete=models.PROTECT )
  name = models.CharField( max_length=50 )
  hostname_pattern = models.CharField( editable=False, max_length=100, default='{blueprint}-{id:06}' )
  blueprint = models.CharField( max_length=50 )
  build_priority = models.IntegerField( default=100 )
  auto_build = models.BooleanField( default=False )
  complex = models.CharField( max_length=50 )
  config_values = MapField()
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
  member_affinity = models.IntegerField( null=True, blank=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @property
  def uid( self ):
    return '{0}:{1}'.format( ( self.site.name, self.name ) )

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

    if not member_name_regex.match( self.name ):
      raise ValidationError( 'Member name "{0}" is invalid'.format( self.name ) )

    if self.scaler_type != 'none' and self.tsd_metric is None:
      raise ValidationError( 'tsd_metric is required if scaler_type is not none' )

    if self.tsd_metric is not None:
      if self.a_value is None or self.b_value is None or self.deadband_margin is None:
        raise ValidationError( 'a_value, b_value, deadband_margin are required when there is a metric' )

    if self.scaler_type == 'linear':
      if self.p_value is None:
        raise ValidationError( 'p_value is required for scaler_type "linear"' )

      if self.p_value == 0:
        raise ValidationError( 'p_value can not be 0 for scaler_type "linear"' )

      if ( self.a_value + self.b_value ) > 1:
        raise ValidationError( 'a_value + b_value can not exceed 1' )

    if self.scaler_type == 'step':
      if self.step_threshold is None:
        raise ValidationError( 'step_threshold is required for scaler_type "step"' )

      if self.step_threshold == 0:
        raise ValidationError( 'step_threshold can not be 0 for scaler_type "step"' )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Member "{0}" in "{1}"'.format( self.name, self.site.pk )

  class Meta:
    unique_together = ( ( 'site', 'name' ), )
