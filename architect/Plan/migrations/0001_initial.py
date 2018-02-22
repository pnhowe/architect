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
            name='DynamicPlanBluePrint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.BluePrint')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicPlanComplex',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.AvailabilityTS', related_name='+')),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.Complex')),
                ('cost', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.CostTS', related_name='+')),
                ('reliability', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.ReliabilityTS', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicPlanTimeSeries',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('timeseries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.RawTimeSeries', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=False)),
                ('change_cooldown', models.IntegerField(help_text='number of seconds to wait after a change before re-evaluating the plan', default=300)),
                ('last_change', models.DateTimeField(blank=True, null=True)),
                ('max_inflight', models.IntegerField(help_text='number of things that can be changing at the same time', default=2)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DynamicPlan',
            fields=[
                ('plan_ptr', models.OneToOneField(primary_key=True, to='Plan.Plan', auto_created=True, serialize=False, parent_link=True)),
                ('hostname_pattern', models.CharField(default='{plan}-{blueprint}-{nonce}', max_length=100)),
                ('config_values', architect.fields.MapField(help_text="Contracor style config values, which are loaded into Contractor's Structure model when the Structure is created", default={}, blank=True)),
                ('script', models.TextField()),
                ('slots_per_complex', models.IntegerField(default=100)),
                ('nonce_counter', models.IntegerField(default=1)),
                ('can_move', models.BooleanField(default=False)),
                ('can_destroy', models.BooleanField(default=False)),
                ('can_build', models.BooleanField(default=True)),
            ],
            bases=('Plan.plan',),
        ),
        migrations.CreateModel(
            name='StaticPlan',
            fields=[
                ('plan_ptr', models.OneToOneField(primary_key=True, to='Plan.Plan', auto_created=True, serialize=False, parent_link=True)),
                ('plan', architect.fields.MapField(default={})),
            ],
            bases=('Plan.plan',),
        ),
        migrations.AddField(
            model_name='dynamicplantimeseries',
            name='plan',
            field=models.ForeignKey(to='Plan.DynamicPlan'),
        ),
        migrations.AddField(
            model_name='dynamicplancomplex',
            name='plan',
            field=models.ForeignKey(to='Plan.DynamicPlan'),
        ),
        migrations.AddField(
            model_name='dynamicplanblueprint',
            name='plan',
            field=models.ForeignKey(to='Plan.DynamicPlan'),
        ),
        migrations.AddField(
            model_name='dynamicplan',
            name='blueprint_list',
            field=models.ManyToManyField(through='Plan.DynamicPlanBluePrint', to='Contractor.BluePrint'),
        ),
        migrations.AddField(
            model_name='dynamicplan',
            name='complex_list',
            field=models.ManyToManyField(through='Plan.DynamicPlanComplex', to='Contractor.Complex'),
        ),
        migrations.AddField(
            model_name='dynamicplan',
            name='timeseries_list',
            field=models.ManyToManyField(through='Plan.DynamicPlanTimeSeries', to='TimeSeries.RawTimeSeries'),
        ),
        migrations.AlterUniqueTogether(
            name='dynamicplantimeseries',
            unique_together=set([('plan', 'timeseries')]),
        ),
        migrations.AlterUniqueTogether(
            name='dynamicplancomplex',
            unique_together=set([('plan', 'complex')]),
        ),
        migrations.AlterUniqueTogether(
            name='dynamicplanblueprint',
            unique_together=set([('plan', 'blueprint')]),
        ),
    ]
