from django.shortcuts import render

from architect.Inspector.models import Inspection

def index( request ):
  return render( request, 'index.html', { 'inspection_list': Inspection.objects.all() } )
