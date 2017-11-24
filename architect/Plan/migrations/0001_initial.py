# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
        ('TimeSeries', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('hostname_pattern', models.CharField(default='{blueprint}-{id:06}', max_length=100, editable=False)),
                ('blueprint', models.CharField(max_length=50)),
                ('build_priority', models.IntegerField(default=100)),
                ('auto_build', models.BooleanField(default=False)),
                ('complex', models.CharField(max_length=50)),
                ('config_values', architect.fields.MapField(default={})),
                ('scaler_type', models.CharField(default='none', max_length=5, choices=[('none', 'None'), ('step', 'Step'), ('linear', 'Linear')])),
                ('min_instances', models.IntegerField(blank=True, null=True)),
                ('max_instances', models.IntegerField(blank=True, null=True)),
                ('build_ahead', models.IntegerField(default=0)),
                ('regenerate_rate', models.IntegerField(default=1)),
                ('tsd_metric', models.CharField(blank=True, max_length=200, null=True)),
                ('lockout_query', models.CharField(blank=True, max_length=200, null=True)),
                ('p_value', models.FloatField(blank=True, null=True)),
                ('a_value', models.FloatField(blank=True, null=True)),
                ('b_value', models.FloatField(blank=True, null=True)),
                ('step_threshold', models.FloatField(blank=True, null=True)),
                ('deadband_margin', models.IntegerField(blank=True, null=True)),
                ('cooldown_seconds', models.IntegerField(default=60)),
                ('can_grow', models.BooleanField(default=False)),
                ('can_shrink', models.BooleanField(default=False)),
                ('member_affinity', models.IntegerField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('script', models.TextField()),
                ('static_values', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanBluePrint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='Plan.BluePrint')),
                ('plan', models.ForeignKey(to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='PlanComplex',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(to='TimeSeries.TimeSeries', related_name='+')),
                ('complex', models.ForeignKey(to='Plan.Complex')),
                ('cost', models.ForeignKey(to='TimeSeries.TimeSeries', related_name='+')),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('reliability', models.ForeignKey(to='TimeSeries.TimeSeries', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='PlanTimeSeries',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='TimeSeries.TimeSeries', related_name='+')),
                ('plan', models.ForeignKey(to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=20)),
                ('description', models.CharField(max_length=200)),
                ('config_values', architect.fields.MapField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(to='Plan.Site', blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='plan',
            name='blueprint_list',
            field=models.ManyToManyField(to='Plan.BluePrint', through='Plan.PlanBluePrint'),
        ),
        migrations.AddField(
            model_name='plan',
            name='complex_list',
            field=models.ManyToManyField(to='Plan.Complex', through='Plan.PlanComplex'),
        ),
        migrations.AddField(
            model_name='plan',
            name='timeseries_list',
            field=models.ManyToManyField(to='TimeSeries.TimeSeries', through='Plan.PlanTimeSeries'),
        ),
        migrations.AddField(
            model_name='member',
            name='site',
            field=models.ForeignKey(to='Plan.Site', editable=False),
        ),
        migrations.AlterUniqueTogether(
            name='plantimeseries',
            unique_together=set([('plan', 'blueprint')]),
        ),
        migrations.AlterUniqueTogether(
            name='plancomplex',
            unique_together=set([('plan', 'complex')]),
        ),
        migrations.AlterUniqueTogether(
            name='planblueprint',
            unique_together=set([('plan', 'blueprint')]),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('site', 'name')]),
        ),
    ]
