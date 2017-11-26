import re

from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

from architect.TimeSeries.libts import getTS

LAST_VALUE_MAX_AGE = 3600  # in seconds

metric_regex = re.compile( '^[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*$' )

cinp = CInP( 'TimeSeries', '0.1' )


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class Complex( models.Model ):

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True


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
    return None

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
  complex = models.ForeignKey( Complex, related_name='+', on_delete=models.CASCADE )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return getTS().graph( 'complex.{0}.cost'.format( self.complex.tsname ), start_offset, end_offset, height, width )

  @property
  def last_value( self ):
    return None

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
  complex = models.ForeignKey( Complex, related_name='+', on_delete=models.CASCADE )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return getTS().graph( 'complex.{0}.availability'.format( self.complex.tsname ), start_offset, end_offset, height, width )

  @property
  def last_value( self ):
    return None

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class ReliabilityTS( TimeSeries ):
  complex = models.ForeignKey( Complex, related_name='+', on_delete=models.CASCADE )

  @property
  def graph_url( self, start_offset, end_offset, height, width ):
    return getTS().graph( 'complex.{0}.reliability'.format( self.complex.tsname ), start_offset, end_offset, height, width )

  @property
  def last_value( self ):
    return None

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True
