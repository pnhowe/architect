# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import architect.fields
import django.db.models.deletion


def create_loader( app, schema_editor ):
    Loader = app.get_model( 'Project', 'Loader' )
    l = Loader( id=1, current_hash='X', upstream_hash='X', last_update=datetime.min.replace( tzinfo=utc ), last_check=datetime.min.replace( tzinfo=utc ) )
    l.full_clean()
    l.save()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('type', models.CharField(max_length=13, choices=[('site', 'site'), ('address_block', 'address_block'), ('structure', 'structure'), ('complex', 'complex'), ('plan', 'plan')])),
                ('action', models.CharField(max_length=13, choices=[('local_create', 'local_create'), ('remote_create', 'remote_create'), ('local_delete', 'local_delete'), ('remote_delete', 'remote_delete'), ('change', 'change')])),
                ('target_id', models.CharField(max_length=50)),
                ('current_val', architect.fields.JSONField(null=True, blank=True)),
                ('target_val', architect.fields.JSONField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Loader',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('current_hash', models.CharField(max_length=40)),
                ('last_update', models.DateTimeField()),
                ('upstream_hash', models.CharField(max_length=40)),
                ('last_check', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('static_entry_map', architect.fields.MapField(blank=True, default={})),
                ('address_block_map', architect.fields.MapField(blank=True, default={})),
                ('last_load_hash', models.CharField(max_length=40)),
                ('last_load', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(to='Project.Site', null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='change',
            name='site',
            field=models.ForeignKey(to='Project.Site', on_delete=django.db.models.deletion.PROTECT, null=True, blank=True, related_name='+'),
        ),
        migrations.RunPython( create_loader ),
    ]
