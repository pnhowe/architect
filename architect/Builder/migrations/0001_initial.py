# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('rebuild', 'rebuild'), ('move', 'move')], max_length=10)),
                ('state', architect.fields.JSONField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('state', models.CharField(choices=[('new', 'new'), ('built', 'built'), ('destroyed', 'destroyed'), ('processing', 'processing')], max_length=10)),
                ('hostname', models.CharField(max_length=200, unique=True)),
                ('nonce', models.CharField(max_length=26, unique=True)),
                ('foundation_id', models.CharField(max_length=100, unique=True, blank=True)),
                ('structure_id', models.IntegerField(null=True, unique=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('target', models.CharField(choices=[('foundation', 'foundation'), ('structure', 'structure')], max_length=10)),
                ('task', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('move', 'move')], max_length=7)),
                ('state', models.CharField(choices=[('new', 'new'), ('waiting', 'waiting'), ('done', 'done'), ('error', 'error')], max_length=7)),
                ('web_hook_token', models.CharField(null=True, max_length=40, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.OneToOneField(to='Builder.Action', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
    ]
