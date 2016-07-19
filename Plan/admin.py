from django.contrib import admin

from architect.Plan.models import Site, Member, Instance

admin.register( Site )
admin.register( Member )
admin.register( Instance )
