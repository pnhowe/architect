# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Contractor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailabilityTS',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.OneToOneField(to='Contractor.Complex')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Controller',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=50)),
                ('scaler_type', models.CharField(choices=[('none', 'None'), ('step', 'Step'), ('linear', 'Linear')], max_length=5, default='none')),
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
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CostTS',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.OneToOneField(to='Contractor.Complex')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RawTimeSeries',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('metric', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReliabilityTS',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.OneToOneField(to='Contractor.Complex')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
