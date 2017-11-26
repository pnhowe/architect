from cinp.client import CInP

from django.conf import settings


def getContractor():
  return Contractor( settings.CONTRACTOR_HOST, settings.CONTRACTOR_ROOT_PATH, settings.CONTRACTOR_PORT, settings.CONTRACTOR_PROXY )


class Contractor():
  def __init__( self, host, root_path, port, proxy=None ):
    super().__init__()
    self.cinp = CInP( host, root_path, port )

  def getComplexes( self ):
    return self.cinp.getFilteredURIs( '/api/v1/Building/Complex' )

  def getBluePrints( self ):
    return self.cinp.getFilteredURIs( '/api/v1/BluePrint/StructureBluePrint' )
