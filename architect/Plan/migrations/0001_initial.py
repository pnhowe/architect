# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
        ('TimeSeries', '0001_initial'),
        ('Contractor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=False)),
                ('hostname_pattern', models.CharField(max_length=100, default='{plan}-{nonce}')),
                ('config_values', architect.fields.MapField(blank=True, default={})),
                ('script', models.TextField()),
                ('static_values', models.TextField(null=True, blank=True)),
                ('slots_per_complex', models.IntegerField(default=100)),
                ('change_cooldown', models.IntegerField(default=300)),
                ('max_inflight', models.IntegerField(default=2)),
                ('last_change', models.DateTimeField()),
                ('nonce_counter', models.IntegerField(default=1)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlanBluePrint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='Contractor.BluePrint', on_delete=django.db.models.deletion.PROTECT)),
                ('plan', models.ForeignKey(to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='PlanComplex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='TimeSeries.AvailabilityTS')),
                ('complex', models.ForeignKey(to='Contractor.Complex', on_delete=django.db.models.deletion.PROTECT)),
                ('cost', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='TimeSeries.CostTS')),
                ('plan', models.ForeignKey(to='Plan.Plan')),
                ('reliability', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='TimeSeries.ReliabilityTS')),
            ],
        ),
        migrations.CreateModel(
            name='PlanTimeSeries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
