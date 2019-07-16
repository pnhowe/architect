from django.conf import settings

from cinp.server_werkzeug import WerkzeugServer

from contractor.Auth.models import getUser

# get plugins

import os
from contractor import plugins

plugin_list = []
plugin_dir = os.path.dirname( plugins.__file__ )
for item in os.scandir( plugin_dir ):
  if not item.is_dir() or not os.path.exists( os.path.join( plugin_dir, item.name, 'models.py' ) ):
    continue
  plugin_list.append( 'contractor.plugins.{0}'.format( item.name ) )


def get_app( debug ):
  app = WerkzeugServer( root_path='/api/v1/', root_version='0.9', debug=debug, get_user=getUser, cors_allow_list=[ '*' ], debug_dump_location=settings.DEBUG_DUMP_LOCATION )

  app.registerNamespace( '/', 'architect.Auth' )
  app.registerNamespace( '/', 'architect.Contractor' )
  app.registerNamespace( '/', 'architect.TimeSeries' )
  app.registerNamespace( '/', 'architect.Builder' )
  app.registerNamespace( '/', 'architect.Plan' )
  app.registerNamespace( '/', 'architect.Project' )
  app.registerNamespace( '/', 'architect.Inspector' )

  app.validate()

  return app
