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

  def getComplex( self, id ):
    complex = self.cinp.get( '/api/v1/Building/Complex:{0}:'.format( id ) )
    complex[ 'site' ] = self.cinp.uri.extractIds( complex[ 'site' ] )[0]
    return complex

  def createStructure( self, complex, blueprint, hostname ):
    structure = self.cinp.call( '/api/v1/Building/Complex:{0}:(createStructure)'.format( complex ), { 'blueprint': '/api/v1/BluePrint/StructureBluePrint:{0}:'.format( blueprint ), 'hostname': hostname } )

    return self.cinp.uri.extractIds( structure )[0]

  def registerWebHook( self, job_id, structure_id, token ):
    data = {}
    data[ 'structure' ] = '/api/v1/Building/Structure:{0}:'.format( structure_id )
    data[ 'one_shot' ] = True
    data[ 'extra_data' ] = { 'token': token }
    data[ 'type' ] = 'call'
    data[ 'url' ] = 'http://127.0.0.1:8880/api/v1/Builder/Job:{0}:(jobNotify)'.format( job_id )
    self.cinp.create( '/api/v1/PostOffice/StructureBox', data )
