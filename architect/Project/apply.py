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

    elif change.action == 'remote_delete':
      contractor = getContractor()
      contractor.deleteStructure( change.target_id )

      result = 'Structure "{0}" deleted remotely'.format( change.target_id )

    else:
      raise ValueError( 'Unknown Action "{0}" for Structure'.format( change.action ) )

  elif change.type == 'complex':
    Complex = apps.get_model( 'Contractor', 'Complex' )
    if change.action == 'local_create':
      complex = Complex( name=change.target_id )
      complex.site = change.site
      complex.full_clean()
      complex.save()

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
    PlanBluePrint = apps.get_model( 'Plan', 'PlanBluePrint' )
    PlanTimeSeries = apps.get_model( 'Plan', 'PlanTimeSeries' )
    Complex = apps.get_model( 'Contractor', 'Complex' )
    BluePrint = apps.get_model( 'Contractor', 'BluePrint' )
    RawTimeSeries = apps.get_model( 'TimeSeries', 'RawTimeSeries' )

    if change.action == 'local_create':
      plan = Plan( name=change.target_id )

      for key in ( 'description', 'address_block', 'enabled', 'change_cooldown', 'config_values', 'max_inflight', 'hostname_pattern', 'script', 'slots_per_complex', 'can_move', 'can_destroy', 'can_build' ):
        try:
          setattr( plan, key, change.target_val[ key ] )
        except KeyError:
          pass

      plan.full_clean()
      plan.save()

      complex_list = change.target_val.get( 'complex_list', [] )
      for complex_name in complex_list:
        try:
          complex = Complex.objects.get( name=complex_name )
        except Complex.DoesNotExist:
          raise ValueError( 'Complex named "{0}" not found'.format( complex_name ) )

        plancomplex = PlanComplex( plan=plan, complex=complex )
        plancomplex.full_clean()
        plancomplex.save()

      blueprint_map = change.target_val.get( 'blueprint_map', {} )
      for script_name, blueprint_name in blueprint_map.items():
        blueprint = PlanBluePrint( plan=plan, script_name=script_name, blueprint=BluePrint.objects.get( name=blueprint_name ) )
        blueprint.full_clean()
        blueprint.save()

      timeseries_map = change.target_val.get( 'timeseries_map', {} )
      for script_name, timeseries_metric in timeseries_map.items():
        try:
          timeseries = RawTimeSeries.objects.get( metric=timeseries_metric )
        except RawTimeSeries.DoesNotExist:
          timeseries = RawTimeSeries( metric=timeseries_metric )
          timeseries.full_clean()
          timeseries.save()

        plantimeseries = PlanTimeSeries( plan=plan, timeseries=timeseries, script_name=script_name )
        plantimeseries.full_clean()
        plantimeseries.save()

      result = 'Plan "{0}" added locally'.format( change.target_id )

    elif change.action == 'change':
      plan = Plan.objects.get( name=change.target_id )

      for key in ( 'description', 'enabled', 'change_cooldown', 'config_values', 'max_inflight', 'hostname_pattern', 'script', 'slots_per_complex', 'can_move', 'can_destroy', 'can_build' ):
        try:
          setattr( plan, key, change.target_val[ key ] )
        except KeyError:
          pass

      plan.full_clean()
      plan.save()

      if 'complex_list' in change.target_val:
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

      if 'blueprint_map' in change.target_val:
        blueprint_list = set( change.target_val.get( 'blueprint_map', {} ).items() )
        cur_blueprint_list = set( [ ( i.script_name, i.blueprint.name ) for i in plan.planblueprint_set.all() ] )
        for script_name, blueprint_name in list( blueprint_list - cur_blueprint_list ):
          try:
            blueprint = BluePrint.objects.get( name=blueprint_name )
          except Complex.DoesNotExist:
            raise ValueError( 'Blueprint named "{0}" not found'.format( blueprint_name ) )

          planblueprint = PlanBluePrint( plan=plan, script_name=script_name, blueprint=blueprint )
          planblueprint.full_clean()
          planblueprint.save()

        for script_name, blueprint_name in list( cur_blueprint_list - blueprint_list ):
          try:
            planblueprint = PlanBluePrint.objects.get( plan=plan, script_name=script_name, blueprint__name=blueprint_name )
          except PlanBluePrint.DoesNotExist:
            continue

          planblueprint.delete()

      if 'timeseries_map' in change.target_val:
        timeseries_list = set( change.target_val.get( 'timeseries_map', {} ).items() )
        cur_timeseries_list = set( [ ( i.script_name, i.timeseries.metric ) for i in plan.plantimeseries_set.all() ] )
        for script_name, timeseries_metric in list( timeseries_list - cur_timeseries_list ):
          try:
            timeseries = RawTimeSeries.objects.get( metric=timeseries_metric )
          except RawTimeSeries.DoesNotExist:
            timeseries = RawTimeSeries( metric=timeseries_metric )
            timeseries.full_clean()
            timeseries.save()

          plantimeseries = PlanTimeSeries( plan=plan, script_name=script_name, timeseries=timeseries )
          plantimeseries.full_clean()
          plantimeseries.save()

        for script_name, timeseries_metric in list( cur_timeseries_list - timeseries_list ):
          try:
            plantimeseries = RawTimeSeries.objects.get( plan=plan, script_name=script_name, timeseries__metric=timeseries_metric )
          except RawTimeSeries.DoesNotExist:
            continue

          plantimeseries.delete()

      result = 'Plan "{0}" updated fields: "{1}"'.format( change.target_id, '", "'.join( change.target_val.keys() ) )

    else:
      raise ValueError( 'Unknown Action "{0}" for Plan'.format( change.action ) )

  else:
    raise ValueError( 'Unknown Action "{0}"'.format( change.type ) )

  return result
