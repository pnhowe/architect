# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Plan', '0001_initial'),
        ('Contractor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('action', models.CharField(max_length=10, choices=[('build', 'build'), ('destroy', 'destroy'), ('rebuild', 'rebuild'), ('move', 'move')])),
                ('state', architect.fields.JSONField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('nonce', models.CharField(max_length=26, unique=True)),
                ('state', models.CharField(max_length=10, choices=[('built', 'built'), ('destroyed', 'destroyed'), ('processing', 'processing')])),
                ('hostname', models.CharField(max_length=200, unique=True)),
                ('foundation_id', models.IntegerField(null=True, blank=True, unique=True)),
                ('structure_id', models.IntegerField(null=True, blank=True, unique=True)),
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
                ('target', models.CharField(max_length=10, choices=[('foundation', 'foundation'), ('structure', 'structure')])),
                ('task', models.CharField(max_length=7, choices=[('build', 'build'), ('destroy', 'destroy'), ('move', 'move')])),
                ('state', models.CharField(max_length=7, choices=[('new', 'new'), ('waiting', 'waiting'), ('done', 'done'), ('error', 'error')])),
                ('web_hook_token', models.CharField(null=True, blank=True, max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='Builder.Action')),
            ],
        ),
        migrations.AddField(
            model_name='action',
            name='instance',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='Builder.Instance'),
        ),
    ]
