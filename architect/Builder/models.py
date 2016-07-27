from django.db import models

from architect.Plan.models import Member

class Instance( models.Model ):
  member = models.ForeignKey( Member, on_delete=models.SET_NULL, null=True, blank=True )
  hostname = models.CharField( max_length=100 )
  structure_id = models.IntegerField( unique=True ) # structure_id on contractor
  offset = models.IntegerField()
  requested_at = models.DateTimeField( null=True, blank=True )
  built_at = models.DateTimeField( null=True, blank=True )
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
      return 'built'

    if not self.destroyed_at and self.unrequested_at:
      return 'removing'

    if self.destroyed_at:
      return 'destroyed'

  @property
  def config_values( self ):
    result = self.member.config_values
    result[ 'offset' ] = self.offset

    return result

  def __str__( self ):
    return 'Instance of "{0}" in "{1}" instance #{3}'.format( self.member.name, self.member.site.pk, self.instance )

  class Meta:
    unique_together = ( ( 'member', 'offset' ), )


class Job( models.Model ):
  JOB_ACTION_CHOICES = ( ( 'build', 'build' ), ( 'destroy', 'destroy' ), ( 'regenerate', 'regenerate' ) )
  instance = models.ForeignKey( Instance, on_delete=models.CASCADE )
  job_id = models.IntegerField() # contractor build job id
  action = models.CharField( max_length=20, choices=JOB_ACTION_CHOICES, default='none' )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )
