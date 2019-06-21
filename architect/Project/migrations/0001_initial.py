# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('type', models.CharField(choices=[('site', 'site'), ('address_block', 'address_block'), ('structure', 'structure'), ('complex', 'complex'), ('plan', 'plan')], max_length=13)),
                ('action', models.CharField(choices=[('local_create', 'local_create'), ('remote_create', 'remote_create'), ('local_delete', 'local_delete'), ('remote_delete', 'remote_delete'), ('change', 'change')], max_length=13)),
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
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('static_entry_map', architect.fields.MapField(default={}, blank=True)),
                ('address_block_map', architect.fields.MapField(default={}, blank=True)),
                ('last_load_hash', models.CharField(max_length=40)),
                ('last_load', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(null=True, blank=True, to='Project.Site')),
            ],
        ),
        migrations.AddField(
            model_name='change',
            name='site',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', blank=True, to='Project.Site'),
        ),
    ]
