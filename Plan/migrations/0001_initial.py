# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('instance', models.IntegerField()),
                ('requested_at', models.DateTimeField(blank=True, null=True)),
                ('build_at', models.DateTimeField(blank=True, null=True)),
                ('unrequested_at', models.DateTimeField(blank=True, null=True)),
                ('destroyed_at', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=100)),
                ('plan', models.CharField(max_length=50)),
                ('build_priority', models.IntegerField(default=100)),
                ('auto_build', models.BooleanField(default=False)),
                ('deploy_to', models.CharField(max_length=50)),
                ('config_values', architect.fields.JSONField()),
                ('scaler_type', models.CharField(choices=[('none', 'None'), ('step', 'Step'), ('liner', 'Liner')], default='none', max_length=5)),
                ('min_instances', models.IntegerField(blank=True, null=True)),
                ('max_instances', models.IntegerField(blank=True, null=True)),
                ('query', models.CharField(blank=True, null=True, max_length=200)),
                ('lockout_query', models.CharField(blank=True, null=True, max_length=200)),
                ('p_value', models.FloatField(blank=True, null=True)),
                ('a_value', models.FloatField(blank=True, null=True)),
                ('b_value', models.FloatField(blank=True, null=True)),
                ('rachet_threshold', models.FloatField(blank=True, null=True)),
                ('deadband_width', models.IntegerField(blank=True, null=True)),
                ('cooldown_seconds', models.IntegerField(default=60)),
                ('can_grow', models.BooleanField(default=False)),
                ('can_shrink', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, max_length=20)),
                ('description', models.CharField(max_length=200)),
                ('config_values', architect.fields.JSONField()),
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
        migrations.AddField(
            model_name='instance',
            name='member',
            field=models.ForeignKey(to='Plan.Member'),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together=set([('site', 'name')]),
        ),
    ]
