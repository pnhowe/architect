# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TimeSeries', '0001_initial'),
        ('Contractor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('name', models.TextField(max_length=200, serialize=False, primary_key=True)),
                ('address_block', models.CharField(max_length=40, help_text='name of the address block, must be the same for each site')),
                ('description', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(help_text='enabled to be scanned and updated that is, any existing resources will not be affected', default=False)),
                ('change_cooldown', models.IntegerField(help_text='number of seconds to wait after a change before re-evaluating the plan', default=300)),
                ('config_values', architect.fields.MapField(blank=True, help_text="Contracor style config values, which are loaded into Contractor's Structure model when the Structure is created", default={})),
                ('last_change', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0))),
                ('max_inflight', models.IntegerField(help_text='number of things that can be changing at the same time', default=2)),
                ('hostname_pattern', models.CharField(max_length=100, default='{plan}-{blueprint}-{nonce}')),
                ('script', models.TextField()),
                ('slots_per_complex', models.IntegerField(default=100)),
                ('nonce_counter', models.IntegerField(default=1)),
                ('can_move', models.BooleanField(default=False)),
                ('can_destroy', models.BooleanField(default=False)),
                ('can_build', models.BooleanField(default=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanBluePrint',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('script_name', models.CharField(max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='Contractor.BluePrint', on_delete=django.db.models.deletion.PROTECT, related_name='+')),
                ('plan', models.ForeignKey(to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='PlanComplex',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.ForeignKey(to='Contractor.Complex', on_delete=django.db.models.deletion.PROTECT, related_name='+')),
                ('plan', models.ForeignKey(to='Plan.Plan', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='PlanTimeSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('timeseries', models.ForeignKey(to='TimeSeries.RawTimeSeries', on_delete=django.db.models.deletion.PROTECT, related_name='+')),
            ],
        ),
        migrations.AddField(
            model_name='plan',
            name='blueprint_list',
            field=models.ManyToManyField(to='Contractor.BluePrint', through='Plan.PlanBluePrint'),
        ),
        migrations.AddField(
            model_name='plan',
            name='complex_list',
            field=models.ManyToManyField(to='Contractor.Complex', through='Plan.PlanComplex'),
        ),
        migrations.AddField(
            model_name='plan',
            name='timeseries_list',
            field=models.ManyToManyField(to='TimeSeries.RawTimeSeries', through='Plan.PlanTimeSeries'),
        ),
        migrations.AlterUniqueTogether(
            name='plantimeseries',
            unique_together=set([('plan', 'timeseries')]),
        ),
        migrations.AlterUniqueTogether(
            name='plancomplex',
            unique_together=set([('plan', 'complex')]),
        ),
        migrations.AlterUniqueTogether(
            name='planblueprint',
            unique_together=set([('plan', 'blueprint', 'script_name')]),
        ),
    ]
