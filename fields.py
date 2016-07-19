import json

from django.db import models
from django.core.exceptions import ValidationError

def validate_json( value ):
  try:
    json.loads( value )
  except ValueError:
    raise ValidationError( '"%(value)s" is  not falid JSON', params={ 'value': value } )

class JSONField( models.TextField ):
  default = '{}'
  validators = [ validate_json ]
