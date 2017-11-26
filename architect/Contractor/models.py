import re

from django.db import models
from django.core.exceptions import ValidationError

from cinp.orm_django import DjangoCInP as CInP

SCALER_CHOICES = ( ( 'none', 'None' ), ( 'step', 'Step' ), ( 'linear', 'Linear' ) )

complex_tsname_regex = re.compile( '^[a-zA-Z][a-zA-Z0-9]+$' )
blueprint_name_regex = re.compile( '^[a-zA-Z][a-zA-Z0-9]+$' )

cinp = CInP( 'Contractor', '0.1' )


@cinp.model( not_allowed_method_list=[ 'DELETE', 'CREATE', 'CALL' ] )
class Complex( models.Model ):
  contractor_id = models.CharField( max_length=40, unique=True, blank=True, null=True )  # TODO: ReadOnly from API
  tsname = models.CharField( max_length=50, unique=True, blank=True, null=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not self.tsname:
      self.tsname = None

    if not self.contractor_id:
      self.contractor_id = None

    errors = {}
    if self.tsname is not None and not complex_tsname_regex.match( self.tsname ):
      errors[ 'tsname' ] = 'tsname "{0}" is invalid'.format( self.tsname )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'Complex, contractor: "{0}" tsname: "{1}"'.format( self.contractor_id, self.tsname )


@cinp.model( not_allowed_method_list=[ 'UPDATE', 'DELETE', 'CREATE', 'CALL' ] )
class BluePrint( models.Model ):
  contractor_id = models.CharField( max_length=40, unique=True, blank=True, null=True )  # TODO: ReadOnly from API
  name = models.CharField( max_length=50, unique=True, blank=True, null=True )
  updated = models.DateTimeField( auto_now=True )
  created = models.DateTimeField( auto_now_add=True )

  def clean( self, *args, **kwargs ):
    super().clean( *args, **kwargs )
    if not self.name:
      self.name = None

    if not self.contractor_id:
      self.contractor_id = None

    errors = {}
    if self.name is not None and not blueprint_name_regex.match( self.name ):
      errors[ 'name' ] = 'name "{0}" is invalid'.format( self.name )

    if errors:
      raise ValidationError( errors )

  @cinp.check_auth()
  @staticmethod
  def checkAuth( user, method, id_list, action=None ):
    return True

  def __str__( self ):
    return 'BluePrint, contractor: "{0}" tsname: "{1}"'.format( self.contractor_id, self.tsname )
