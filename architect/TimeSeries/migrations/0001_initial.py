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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
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
                ('name', models.CharField(primary_key=True, serialize=False, max_length=50)),
                ('scaler_type', models.CharField(default='none', choices=[('none', 'None'), ('step', 'Step'), ('linear', 'Linear')], max_length=5)),
                ('min_instances', models.IntegerField(null=True, blank=True)),
                ('max_instances', models.IntegerField(null=True, blank=True)),
                ('build_ahead', models.IntegerField(default=0)),
                ('regenerate_rate', models.IntegerField(default=1)),
                ('tsd_metric', models.CharField(null=True, blank=True, max_length=200)),
                ('lockout_query', models.CharField(null=True, blank=True, max_length=200)),
                ('p_value', models.FloatField(null=True, blank=True)),
                ('a_value', models.FloatField(null=True, blank=True)),
                ('b_value', models.FloatField(null=True, blank=True)),
                ('step_threshold', models.FloatField(null=True, blank=True)),
                ('deadband_margin', models.IntegerField(null=True, blank=True)),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('complex', models.OneToOneField(to='Contractor.Complex')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
