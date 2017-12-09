# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Plan', '0001_initial'),
        ('Contractor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('nonce', models.CharField(unique=True, max_length=26)),
                ('hostname', models.CharField(unique=True, max_length=200)),
                ('contractor_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('requested_at', models.DateTimeField(blank=True, null=True)),
                ('built_at', models.DateTimeField(blank=True, null=True)),
                ('unrequested_at', models.DateTimeField(blank=True, null=True)),
                ('destroyed_at', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.BluePrint')),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.Complex')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Plan.Plan')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('rebuild', 'rebuild'), ('move', 'move')], max_length=7)),
                ('state', models.CharField(choices=[('new', 'new'), ('waiting', 'waiting'), ('done', 'done'), ('error', 'error')], max_length=7)),
                ('web_hook_token', models.CharField(blank=True, null=True, max_length=30)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('instance', models.OneToOneField(to='Builder.Instance')),
            ],
        ),
    ]
