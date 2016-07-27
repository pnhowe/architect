import json

from django.db import models
from django.core.exceptions import ValidationError

def validate_json( value ):
  if not isinstance( value, dict ):
    raise ValidationError( 'Value must be a python dict, got %{type}', type=type( dict ).__name__ )

class JSONField( models.TextField ):
  description = 'jSON Encoded'
  validators = [ validate_json ]

  def __init__( self, *args, **kwargs ):
    if 'default' not in kwargs:
      kwargs[ 'default' ] = {}
    super( JSONField, self).__init__( *args, **kwargs )

  def from_db_value( self, value, expression, connection, context ):
    if value is None:
      return value

    try:
      return json.loads( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

  def to_python( self, value ):
    if isinstance( value, dict ):
      return value

    if value is None:
      return value

    try:
      return json.loads( value )
    except ValueError:
      raise ValidationError( '"%(value)s" is not valid JSON', params={ 'value': value[ 0:100 ] } )

  def get_prep_value( self, value ):
    return json.dumps( value )
