from datetime import datetime, timezone

from architect.Contractor.libcontractor import getContractor


def applyChange( change ):
  if self.type == 'site':
    if self.action == 'local_create':
      site = Site( name=self.target_id )
      site.last_load = datetime.now( timezone.utc )
      site.last_load_hash = 'new'
      site.full_clean()
      site.save()

      result = 'Site "{0}" added locally'.format( self.target_id )

    elif self.action == 'remote_create':
      contractor = getContractor()
      contractor.createSite( self.target_id, **self.target_val )

      result = 'Site "{0}" added remotely'.format( self.target_id )

    elif self.action == 'change':
      contractor = getContractor()
      contractor.updateSite( self.target_id, **self.target_val )

      result = 'Site "{0}" updated fields: "{1}"'.format( self.target_id, '", "'.join( self.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for site'.format( self.action ) )

  elif self.type == 'address_block':
    if self.action == 'remote_create':
      contractor = getContractor()
      contractor.createAddressBlock( self.site.name, self.target_id, **self.target_val )

      result = 'Address Block "{0}" added remotely'.format( self.target_id )

    elif self.action == 'change':
      contractor = getContractor()
      contractor.updateAddressBlock( self.target_id, **self.target_val )

      result = 'Address Block "{0}" updated fields: "{1}"'.format( self.target_id, '", "'.join( self.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for address_block'.format( self.action ) )

  elif self.type == 'instance':
    if self.action == 'remote_create':
      contractor = getContractor()
      contractor.createInstance( self.site.name, self.target_id, **self.target_val )

      result = 'Instance "{0}" added remotely'.format( self.target_id )

    elif self.action == 'change':
      contractor = getContractor()
      contractor.updateInstance( self.target_id, **self.target_val )

      result = 'Instance "{0}" updated fields: "{1}"'.format( self.target_id, '", "'.join( self.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for instance'.format( self.action ) )

  else:
    raise ValueError( 'Unknown Action "{0}"'.format( self.type ) )
