# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Contractor', '0001_initial'),
        ('TimeSeries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicPlanBluePrint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.BluePrint')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicPlanComplex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('script_name', models.CharField(max_length=50)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('timeseries', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='TimeSeries.RawTimeSeries', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=50)),
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
                ('change_cooldown', models.IntegerField(default=300, help_text='number of seconds to wait after a change before re-evaluating the plan')),
                ('config_values', architect.fields.MapField(blank=True, default={}, help_text="Contracor style config values, which are loaded into Contractor's Structure model when the Structure is created")),
                ('last_change', models.DateTimeField(blank=True, null=True)),
                ('max_inflight', models.IntegerField(default=2, help_text='number of things that can be changing at the same time')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='site',
            name='parent',
            field=models.ForeignKey(null=True, to='Plan.Site', blank=True),
        ),
        migrations.CreateModel(
            name='DynamicPlan',
            fields=[
                ('plan_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, to='Plan.Plan', primary_key=True)),
                ('hostname_pattern', models.CharField(default='{plan}-{blueprint}-{nonce}', max_length=100)),
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
                ('plan_ptr', models.OneToOneField(parent_link=True, auto_created=True, serialize=False, to='Plan.Plan', primary_key=True)),
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
            field=models.ManyToManyField(to='Contractor.BluePrint', through='Plan.DynamicPlanBluePrint'),
        ),
        migrations.AddField(
            model_name='dynamicplan',
            name='complex_list',
            field=models.ManyToManyField(to='Contractor.Complex', through='Plan.DynamicPlanComplex'),
        ),
        migrations.AddField(
            model_name='dynamicplan',
            name='timeseries_list',
            field=models.ManyToManyField(to='TimeSeries.RawTimeSeries', through='Plan.DynamicPlanTimeSeries'),
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
