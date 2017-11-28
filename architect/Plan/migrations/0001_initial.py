# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Contractor', '0001_initial'),
        ('TimeSeries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('hostname_pattern', models.CharField(default='{blueprint}-{id:06}', editable=False, max_length=100)),
                ('blueprint', models.CharField(max_length=50)),
                ('build_priority', models.IntegerField(default=100)),
                ('auto_build', models.BooleanField(default=False)),
                ('complex', models.CharField(max_length=50)),
                ('config_values', architect.fields.MapField(default={})),
                ('scaler_type', models.CharField(default='none', choices=[('none', 'None'), ('step', 'Step'), ('linear', 'Linear')], max_length=5)),
                ('min_instances', models.IntegerField(null=True, blank=True)),
                ('max_instances', models.IntegerField(null=True, blank=True)),
                ('build_ahead', models.IntegerField(default=0)),
                ('regenerate_rate', models.IntegerField(default=1)),
                ('tsd_metric', models.CharField(max_length=200, null=True, blank=True)),
                ('lockout_query', models.CharField(max_length=200, null=True, blank=True)),
                ('p_value', models.FloatField(null=True, blank=True)),
                ('a_value', models.FloatField(null=True, blank=True)),
                ('b_value', models.FloatField(null=True, blank=True)),
                ('step_threshold', models.FloatField(null=True, blank=True)),
                ('deadband_margin', models.IntegerField(null=True, blank=True)),
                ('cooldown_seconds', models.IntegerField(default=60)),
                ('can_grow', models.BooleanField(default=False)),
                ('can_shrink', models.BooleanField(default=False)),
                ('member_affinity', models.IntegerField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('name', models.CharField(serialize=False, max_length=50, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=False)),
                ('script', models.TextField()),
                ('static_values', models.TextField(null=True, blank=True)),
                ('slots_per_complex', models.IntegerField(default=100)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanBluePrint',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.BluePrint')),
                ('plan', models.ForeignKey(to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='PlanComplex',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(to='TimeSeries.AvailabilityTS', related_name='+', on_delete=django.db.models.deletion.PROTECT)),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.Complex')),
                ('cost', models.ForeignKey(to='TimeSeries.CostTS', related_name='+', on_delete=django.db.models.deletion.PROTECT)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('reliability', models.ForeignKey(to='TimeSeries.ReliabilityTS', related_name='+', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='PlanTimeSeries',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('timeseries', models.ForeignKey(to='TimeSeries.RawTimeSeries', related_name='+', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(serialize=False, max_length=20, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('config_values', architect.fields.MapField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(null=True, to='Plan.Site', on_delete=django.db.models.deletion.PROTECT, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='plan',
            name='blueprint_list',
            field=models.ManyToManyField(through='Plan.PlanBluePrint', to='Contractor.BluePrint'),
        ),
        migrations.AddField(
            model_name='plan',
            name='complex_list',
            field=models.ManyToManyField(through='Plan.PlanComplex', to='Contractor.Complex'),
        ),
        migrations.AddField(
            model_name='plan',
            name='timeseries_list',
            field=models.ManyToManyField(through='Plan.PlanTimeSeries', to='TimeSeries.RawTimeSeries'),
        ),
        migrations.AddField(
            model_name='member',
            name='site',
            field=models.ForeignKey(to='Plan.Site', on_delete=django.db.models.deletion.PROTECT, editable=False),
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
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('site', 'name')]),
        ),
    ]
