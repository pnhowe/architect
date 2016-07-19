import re

from django.db import models
from django.core.exceptions import ValidationError

from architect.lib.libts import getTS
from architect.fields import JSONField

SCALER_CHOICES = ( ( 'none', 'None' ), ( 'step', 'Step' ), ( 'liner', 'Liner' ) )

name_regex = re.compile( '^[a-zA-Z0-9_]*$')

class Site( models.Model ):
  name = models.CharField( max_length=20, primary_key=True ) # same length as contractor.site.name
  description = models.CharField( max_length=200 )
  parent = models.ForeignKey( 'self', null=True, blank=True )
  config_values = JSONField()
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not name_regex.match( self.name ):
      raise ValidationError( 'Site name "{0}" is invalid'.format( self.name ) )

  def __str__( self ):
    return 'Site "{0}"({1})'.format( self.description, self.name )

class Member( models.Model ): # this fields should match the default member in lib.py
  """
config_profile, config_priority, config_values, auto_configure -> values to configure plato with
deploy_to -> if there is a vmhost to deploy to
min/max_instance -> control the limits
query -> query to get from data source
lockout_query -> if this query returns != 0, no adjustment  is allowed
a_value, b_value -> for value prediction. None -> no prediction, ie t+1 = t
p_value -> for linter
rachet_threshold -> for step mode
deadband_with ->
cooldown_seconds -> delay after change before allowing more, to keep thing from  overreacting
can_grow -> allowed to grow
can_shrink -> allowed to shrink
  """
  site = models.ForeignKey( Site, editable=False )
  name = models.CharField( editable=False, max_length=100 )
  blueprint = models.CharField( max_length=50 )
  build_priority = models.IntegerField( default=100 )
  auto_build = models.BooleanField( default=False )
  complex = models.CharField( max_length=50 )
  config_values = JSONField()
  scaler_type = models.CharField( max_length=5, choices=SCALER_CHOICES, default='none' )
  min_instances = models.IntegerField( null=True, blank=True )
  max_instances = models.IntegerField( null=True, blank=True )
  query = models.CharField( max_length=200, null=True, blank=True )
  lockout_query = models.CharField( max_length=200, null=True, blank=True )
  p_value = models.FloatField( null=True, blank=True )
  a_value = models.FloatField( null=True, blank=True )
  b_value = models.FloatField( null=True, blank=True )
  rachet_threshold = models.FloatField( null=True, blank=True )
  deadband_width = models.IntegerField( null=True, blank=True )
  cooldown_seconds = models.IntegerField( default=60 )
  can_grow = models.BooleanField( default=False )
  can_shrink = models.BooleanField( default=False )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @property
  def uid( self ):
    return '%s:%s' % ( self.site.name, self.name )

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
    if not name_regex.match( self.name ):
      raise ValidationError( 'Member name "{0}" is invalid'.format( self.name ) )

    if self.scaler_type == 'liner':
      if self.p_value is None or self.a_value is None or self.b_value is None or self.deadband_width is None:
        raise ValidationError( 'p_value, a_value, b_value, deadband_width are required' )

      if self.p_value == 0:
        raise ValidationError( 'p_value can not be 0' )

      if ( self.a_value + self.b_value ) > 1:
        raise ValidationError( 'a_value + b_value can not exceed 1' )

  def delete( self, *args, **kwargs ):
    getTS.cleanup( self.uid )
    super().delete( *args, **kwargs )

  def __str__( self ):
    return 'Member "{0}" in "{1}"'.format( self.name, self.site.pk )

  class Meta:
    unique_together = ( ( 'site', 'name' ), )


class Instance( models.Model ):
  member = models.ForeignKey( Member )
  instance = models.IntegerField()
  requested_at = models.DateTimeField( null=True, blank=True )
  build_at = models.DateTimeField( null=True, blank=True )
  unrequested_at = models.DateTimeField( null=True, blank=True )
  destroyed_at = models.DateTimeField( null=True, blank=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @property
  def state( self ):
    if not self.destroyed_at and not self.unrequested_at and not self.build_at and not self.requested_at:
      return 'new'

    if not self.destroyed_at and not self.unrequested_at and not self.build_at and self.requested_at:
      return 'requested'

    if not self.destroyed_at and not self.unrequested_at and self.build_at:
      return 'provisioned'

    if not self.destroyed_at and self.unrequested_at:
      return 'removing'

    if self.destroyed_at:
      return 'deprovisioned'

  def __str__( self ):
    return 'Instance of "{0}" in "{1}" instance #{3}'.format( self.member.name, self.member.site.pk, self.instance )
