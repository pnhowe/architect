# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('hostname_pattern', models.CharField(default='{blueprint}-{id:06}', max_length=100, editable=False)),
                ('blueprint', models.CharField(max_length=50)),
                ('build_priority', models.IntegerField(default=100)),
                ('auto_build', models.BooleanField(default=False)),
                ('complex', models.CharField(max_length=50)),
                ('config_values', architect.fields.JSONField(default={})),
                ('scaler_type', models.CharField(default='none', max_length=5, choices=[('none', 'None'), ('step', 'Step'), ('liner', 'Liner')])),
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
            name='Site',
            fields=[
                ('name', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('config_values', architect.fields.JSONField(default={})),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, to='Plan.Site')),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='site',
            field=models.ForeignKey(to='Plan.Site', editable=False),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('site', 'name')]),
        ),
    ]
