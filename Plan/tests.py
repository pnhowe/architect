from django.test import TestCase
from django.core.exceptions import ValidationError

from architect.Plan.models import Site

class ClusterTestCase( TestCase ):
  def setUp( self ):
    pass

  def test_json( self ):
    with self.assertRaises( ValidationError ):
      Site.objects.create( name='test', description='my test', config_values='NOT VALID JSON' )

# validate valid JSON
# validate name, description, config_values(optional) are present
# validate name is valid
# validate name is not duplicated
# validate config_values is a dict
