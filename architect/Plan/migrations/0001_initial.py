# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Contractor', '0001_initial'),
        ('Project', '0001_initial'),
        ('TimeSeries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('name', models.TextField(primary_key=True, max_length=200, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=False)),
                ('change_cooldown', models.IntegerField(default=300, help_text='number of seconds to wait after a change before re-evaluating the plan')),
                ('config_values', architect.fields.MapField(default={}, blank=True, help_text="Contracor style config values, which are loaded into Contractor's Structure model when the Structure is created")),
                ('last_change', models.DateTimeField(auto_now_add=True)),
                ('max_inflight', models.IntegerField(default=2, help_text='number of things that can be changing at the same time')),
                ('hostname_pattern', models.CharField(default='{plan}-{blueprint}-{nonce}', max_length=100)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='Contractor.BluePrint', on_delete=django.db.models.deletion.PROTECT)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='PlanComplex',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.ForeignKey(to='Contractor.Complex', on_delete=django.db.models.deletion.PROTECT)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='PlanTimeSeries',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('timeseries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='TimeSeries.RawTimeSeries')),
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
            name='site',
            field=models.ForeignKey(to='Project.Site'),
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
            unique_together=set([('plan', 'blueprint')]),
        ),
    ]
