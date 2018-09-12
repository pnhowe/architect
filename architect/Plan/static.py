
from architect.Builder.models import Instance

this is all dead?

def caculateChangePlanStatic( plan ):
  result = []
  target = set( plan.plan[ 'instance' ].keys() )
  current = set( Instance.objects.filter( plan=plan ).values_list( 'hostname', flat=True ) )

  print( target )
  print( current )

  for item in target - current:
    print( 'adding "{0}"'.format( item ) )
    tmp = plan.plan[ 'instance' ][ item ]
    print( tmp )
    address = tmp[ 'address_list' ][0]
    result.append( ( 'create', 'typed', plan.name, tmp[ 'type' ], tmp[ 'blueprint' ], item, address[ 'address_block' ], address[ 'offset' ] ) )

  for item in current - target:
    print( 'removing "{0}"'.format( item ) )
    result.append( ( 'destroy', Instance.objects.get( pk=item ) ) )

  return result
