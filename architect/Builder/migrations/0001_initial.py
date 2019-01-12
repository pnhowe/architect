# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Plan', '0001_initial'),
        ('Contractor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('action', models.CharField(max_length=10, choices=[('build', 'build'), ('destroy', 'destroy'), ('rebuild', 'rebuild'), ('move', 'move')])),
                ('state', architect.fields.JSONField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('state', models.CharField(max_length=10, choices=[('new', 'new'), ('built', 'built'), ('destroyed', 'destroyed'), ('processing', 'processing')])),
                ('hostname', models.CharField(max_length=200, unique=True)),
                ('nonce', models.CharField(max_length=26, unique=True)),
                ('foundation_id', models.IntegerField(null=True, unique=True, blank=True)),
                ('structure_id', models.IntegerField(null=True, unique=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('blueprint', models.ForeignKey(to='Contractor.BluePrint', on_delete=django.db.models.deletion.PROTECT)),
                ('complex', models.ForeignKey(to='Contractor.Complex', on_delete=django.db.models.deletion.PROTECT)),
                ('plan', models.ForeignKey(to='Plan.Plan', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('target', models.CharField(max_length=10, choices=[('foundation', 'foundation'), ('structure', 'structure')])),
                ('task', models.CharField(max_length=7, choices=[('build', 'build'), ('destroy', 'destroy'), ('move', 'move')])),
                ('state', models.CharField(max_length=7, choices=[('new', 'new'), ('waiting', 'waiting'), ('done', 'done'), ('error', 'error')])),
                ('web_hook_token', models.CharField(null=True, max_length=40, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.OneToOneField(to='Builder.Action', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AddField(
            model_name='action',
            name='instance',
            field=models.OneToOneField(to='Builder.Instance', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
