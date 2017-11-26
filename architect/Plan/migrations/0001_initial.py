# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TimeSeries', '0001_initial'),
        ('Contractor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('hostname_pattern', models.CharField(editable=False, default='{blueprint}-{id:06}', max_length=100)),
                ('blueprint', models.CharField(max_length=50)),
                ('build_priority', models.IntegerField(default=100)),
                ('auto_build', models.BooleanField(default=False)),
                ('complex', models.CharField(max_length=50)),
                ('config_values', architect.fields.MapField(default={})),
                ('scaler_type', models.CharField(choices=[('none', 'None'), ('step', 'Step'), ('linear', 'Linear')], default='none', max_length=5)),
                ('min_instances', models.IntegerField(blank=True, null=True)),
                ('max_instances', models.IntegerField(blank=True, null=True)),
                ('build_ahead', models.IntegerField(default=0)),
                ('regenerate_rate', models.IntegerField(default=1)),
                ('tsd_metric', models.CharField(blank=True, null=True, max_length=200)),
                ('lockout_query', models.CharField(blank=True, null=True, max_length=200)),
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
                ('name', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=False)),
                ('script', models.TextField()),
                ('static_values', models.TextField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanBluePrint',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.AvailabilityTS')),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.Complex')),
                ('cost', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.CostTS')),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('reliability', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.ReliabilityTS')),
            ],
        ),
        migrations.CreateModel(
            name='PlanTimeSeries',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('timeseries', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.RawTimeSeries')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=20)),
                ('description', models.CharField(max_length=200)),
                ('config_values', architect.fields.MapField(blank=True, default={})),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, to='Plan.Site', on_delete=django.db.models.deletion.PROTECT)),
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
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='Plan.Site'),
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
