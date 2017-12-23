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

  def createFoundation( self, complex, blueprint, hostname ):
    foundation = self.cinp.call( '/api/v1/Building/Complex:{0}:(createFoundation)'.format( complex ), { 'hostname': hostname } )
    print( '************************ created "{0}"'.format( foundation ) )

    foundation_id = self.cinp.uri.extractIds( foundation )[0]
    return foundation_id

  def buildFoundation( self, id ):
    # we have to set locate manually b/c the structure is not auto-configure, at
    # this point contractor dosen't autolocate foundations for non auto-configure structures.
    # we are setting Located here so that a job dosen't get auto created before we
    # can trigger the creation event, techinically there is still a  small hole that
    #  a job can be built.  TODO: tweek foundatino so that it isn't auto built,
    # would be nice if that also made it so we didn't have to setLocated
    self.cinp.call( '/api/v1/Building/Foundation:{0}:(setLocated)'.format( id ), {} )
    job_id = self.cinp.call( '/api/v1/Building/Foundation:{0}:(doCreate)'.format( id ), {} )
    print( '------------------------- create Job foundation "{0}"'.format( job_id ) )

  def destroyFoundation( self, id ):
    self.cinp.call( '/api/v1/Building/Foundation:{0}:(doDestroy)'.format( id ), {} )

  def createStructure( self, site_id, foundation_id, blueprint, hostname, config_values ):
    data = {}
    data[ 'site' ] = '/api/v1/Site/Site:{0}:'.format( site_id )
    data[ 'foundation' ] = '/api/v1/Building/Foundation:{0}:'.format( foundation_id )
    data[ 'hostname' ] = hostname
    data[ 'blueprint' ] = '/api/v1/BluePrint/StructureBluePrint:{0}:'.format( blueprint )
    data[ 'config_values' ] = config_values
    data[ 'auto_build' ] = False

    structure = self.cinp.create( '/api/v1/Building/Structure'.format( complex ), data )
    print( '************************  created "{0}"'.format( structure ) )
    return self.cinp.uri.extractIds( structure[0] )[0]

  def buildStructure( self, id ):
    job_id = self.cinp.call( '/api/v1/Building/Structure:{0}:(doCreate)'.format( id ), {} )
    print( '------------------------- create Job structure "{0}"'.format( job_id ) )

  def destroyStructure( self, id ):
    self.cinp.call( '/api/v1/Building/Structure:{0}:(doDestroy)'.format( id ), {} )

  def registerWebHook( self, target, job_id, target_id, token ):
    data = {}
    data[ target ] = '/api/v1/Building/{0}:{1}:'.format( target.title(), target_id )
    data[ 'one_shot' ] = True
    data[ 'extra_data' ] = { 'token': token, 'target': target }
    data[ 'type' ] = 'call'
    data[ 'url' ] = 'http://127.0.0.1:8880/api/v1/Builder/Job:{0}:(jobNotify)'.format( job_id )
    if target == 'foundation':
      self.cinp.create( '/api/v1/PostOffice/FoundationBox', data )
    else:
      self.cinp.create( '/api/v1/PostOffice/StructureBox', data )
