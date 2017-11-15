from django.db import models

from cinp.orm_django import DjangoCInP as CInP

from architect.Plan.models import Member
from architect.fields import JSONField

from architect.Inspector.libts import getTS


cinp = CInP( 'Inspector', '0.1' )


@cinp.model( property_list=[ 'target_range', 'graph_url', 'building', 'destroying' ], not_allowed_method_list=[ 'DELETE', 'CREATE', 'CALL', 'UPDATE' ] )
class Inspection( models.Model ):
  member = models.OneToOneField( Member, primary_key=True, on_delete=models.CASCADE )
  state = JSONField()
  target_count = models.IntegerField( default=0 )
  next_check = models.DateTimeField()
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  @property
  def target_range( self ):
    if self.member.deadband_margin is None:
      return ( None, None )
    return ( max( 0, self.target_count - self.member.deadband_margin ), self.target_count + self.member.deadband_margin )

  # these three are for the temporary visulation, may keep them may not?
  @property
  def graph_url( self ):
    ts = getTS()
    return ts.getGraph( self.member.uid, "30", "0", 400, 800 )

  @property
  def building( self ):
    return 0

  @property
  def destroying( self ):
    return 0

  ######

  def logCheckpoint( self, timestamp, value, normalized ):
    ts = getTS()
    ( deadband_low, deadband_high ) = self.target_range
    ts.putCheckpoint( self.member.uid, timestamp, value, normalized, self.target_count, self.member.max_instances, self.member.min_instances, deadband_low, deadband_high )

  def logProvisionedState( self, timestamp, active, provisioning, deprovisioining ):
    ts = getTS()
    ts.putProvisionedState( self.member.uid, timestamp, active, provisioning, deprovisioining )

  def delete( self, *args, **kwargs ):
    getTS.cleanup( self.member.uid )
    super().delete( *args, **kwargs )

  def __str__( self ):
    return 'Inspection for "{0}"'.format( self.member )
