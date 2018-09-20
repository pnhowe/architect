from datetime import datetime, timezone
from django.apps import apps

from architect.Contractor.Contractor import getContractor

from architect.TimeSeries.models import CostTS, AvailabilityTS, ReliabilityTS


def applyChange( change ):
  if change.type == 'site':
    Site = apps.get_model( 'Project', 'Site' )

    if change.action == 'local_create':
      site = Site( name=change.target_id )
      site.last_load = datetime.now( timezone.utc )
      site.last_load_hash = 'new'
      site.full_clean()
      site.save()

      result = 'Site "{0}" added locally'.format( change.target_id )

    elif change.action == 'remote_create':
      contractor = getContractor()
      contractor.createSite( change.target_id, **change.target_val )

      result = 'Site "{0}" added remotely'.format( change.target_id )

    elif change.action == 'change':
      contractor = getContractor()
      contractor.updateSite( change.target_id, **change.target_val )

      result = 'Site "{0}" updated fields: "{1}"'.format( change.target_id, '", "'.join( change.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for site'.format( change.action ) )

  elif change.type == 'address_block':
    if change.action == 'remote_create':
      contractor = getContractor()
      contractor.createAddressBlock( change.site.name, change.target_id, **change.target_val )

      result = 'Address Block "{0}" added remotely'.format( change.target_id )

    elif change.action == 'change':
      contractor = getContractor()
      contractor.updateAddressBlock( change.target_id, **change.target_val )

      result = 'Address Block "{0}" updated fields: "{1}"'.format( change.target_id, '", "'.join( change.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for address_block'.format( change.action ) )

  elif change.type == 'structure':
    if change.action == 'remote_create':
      contractor = getContractor()
      contractor.createStructure( change.site.name, change.target_id, **change.target_val )

      result = 'Structure "{0}" added remotely'.format( change.target_id )

    elif change.action == 'change':
      contractor = getContractor()
      contractor.updateStructure( change.target_id, **change.target_val )

      result = 'Structure "{0}" updated fields: "{1}"'.format( change.target_id, '", "'.join( change.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for Structure'.format( change.action ) )

  elif change.type == 'complex':
    Complex = apps.get_model( 'Contractor', 'Complex' )
    if change.action == 'local_create':
      cplx = Complex( name=change.target_id )
      cplx.site = change.site
      cplx.full_clean()
      cplx.save()

      costts = CostTS( complex=complex )
      costts.save()
      availts = AvailabilityTS( complex=complex )
      availts.save()
      reliabts = ReliabilityTS( complex=complex )
      reliabts.save()

      result = 'Complex "{0}" added locally'.format( change.target_id )

    elif change.action == 'remote_create':
      contractor = getContractor()
      contractor.createComplex( change.site.name, change.target_id, **change.target_val )

      result = 'Complex "{0}" added remotely'.format( change.target_id )

    elif change.action == 'change':
      contractor = getContractor()
      contractor.updateComplex( change.target_id, **change.target_val )

      result = 'Complex "{0}" updated fields: "{1}"'.format( change.target_id, '", "'.join( change.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for Complex'.format( change.action ) )

  elif change.type == 'plan':
    Plan = apps.get_model( 'Plan', 'Plan' )
    PlanComplex = apps.get_model( 'Plan', 'PlanComplex' )
    Complex = apps.get_model( 'Contractor', 'Complex' )

    if change.action == 'local_create':
      plan = Plan( name=change.target_id )
      plan.site = change.site

      for key in ( 'description', 'enabled', 'change_cooldown', 'config_values', 'max_inflight', 'hostname_pattern', 'script', 'slots_per_complex', 'can_move', 'can_destroy', 'can_build' ):
        try:
          setattr( plan, key, change.target_val[ key ] )
        except KeyError:
          pass

      plan.full_clean()
      plan.save()

      complex_list = change.target_val.get( 'complex_list', [] )
      for complex_name in complex_list:
        try:
          complex = Complex.objects.get( name=complex )
        except Complex.DoesNotExist:
          raise ValueError( 'Complex named "{0}" not found'.format( complex_name ) )

        plancomplex = PlanComplex( plan=plan, complex=complex )
        plancomplex.full_clean()
        plancomplex.save()

      result = 'Plan "{0}" added locally'.format( change.target_id )

    elif change.action == 'change':
      plan = Plan.objects.get( site=change.site, name=change.target_id )

      for key in ( 'description', 'enabled', 'change_cooldown', 'config_values', 'max_inflight', 'hostname_pattern', 'script', 'slots_per_complex', 'can_move', 'can_destroy', 'can_build' ):
        try:
          setattr( plan, key, change.target_val[ key ] )
        except KeyError:
          pass

      plan.full_clean()
      plan.save()

      complex_list = set( change.target_val.get( 'complex_list', [] ) )
      cur_complex_list = set( [ i.name for i in plan.complex_list.all() ] )
      for complex_name in list( complex_list - cur_complex_list ):
        try:
          complex = Complex.objects.get( name=complex_name )
        except Complex.DoesNotExist:
          raise ValueError( 'Complex named "{0}" not found'.format( complex_name ) )

        plancomplex = PlanComplex( plan=plan, complex=complex )
        plancomplex.full_clean()
        plancomplex.save()

      for complex_name in list( cur_complex_list - complex_list ):
        try:
          plancomplex = PlanComplex.objects.get( plan=plan, complex__name=complex_name )
        except PlanComplex.DoesNotExist:
          continue

        plancomplex.delete()

      result = 'Plan "{0}" updated fields: "{1}"'.format( change.target_id, '", "'.join( change.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for Plan'.format( change.action ) )

  else:
    raise ValueError( 'Unknown Action "{0}"'.format( change.type ) )

  return result
