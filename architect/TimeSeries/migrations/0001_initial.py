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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
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
                ('name', models.CharField(primary_key=True, max_length=50, serialize=False)),
                ('scaler_type', models.CharField(default='none', choices=[('none', 'None'), ('step', 'Step'), ('linear', 'Linear')], max_length=5)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.OneToOneField(to='Contractor.Complex')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
