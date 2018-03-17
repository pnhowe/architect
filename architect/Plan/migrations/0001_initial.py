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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.BluePrint')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicPlanComplex',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('availability', models.ForeignKey(related_name='+', to='TimeSeries.AvailabilityTS', on_delete=django.db.models.deletion.PROTECT)),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.Complex')),
                ('cost', models.ForeignKey(related_name='+', to='TimeSeries.CostTS', on_delete=django.db.models.deletion.PROTECT)),
                ('reliability', models.ForeignKey(related_name='+', to='TimeSeries.ReliabilityTS', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='DynamicPlanTimeSeries',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('timeseries', models.ForeignKey(related_name='+', to='TimeSeries.RawTimeSeries', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(serialize=False, max_length=50, primary_key=True)),
                ('static_entry_map', architect.fields.MapField(blank=True, default={})),
                ('address_block_map', architect.fields.MapField(blank=True, default={})),
                ('last_load_hash', models.CharField(max_length=40)),
                ('last_load', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('site', models.OneToOneField(serialize=False, to='Plan.Site', primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=False)),
                ('change_cooldown', models.IntegerField(help_text='number of seconds to wait after a change before re-evaluating the plan', default=300)),
                ('config_values', architect.fields.MapField(help_text="Contracor style config values, which are loaded into Contractor's Structure model when the Structure is created", blank=True, default={})),
                ('last_change', models.DateTimeField(null=True, blank=True)),
                ('max_inflight', models.IntegerField(help_text='number of things that can be changing at the same time', default=2)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='site',
            name='parent',
            field=models.ForeignKey(to='Plan.Site', null=True, blank=True),
        ),
        migrations.CreateModel(
            name='DynamicPlan',
            fields=[
                ('plan_ptr', models.OneToOneField(serialize=False, to='Plan.Plan', parent_link=True, auto_created=True, primary_key=True)),
                ('hostname_pattern', models.CharField(max_length=100, default='{plan}-{blueprint}-{nonce}')),
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
                ('plan_ptr', models.OneToOneField(serialize=False, to='Plan.Plan', parent_link=True, auto_created=True, primary_key=True)),
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
