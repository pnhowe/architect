# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Contractor', '0001_initial'),
        ('Plan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('rebuild', 'rebuild'), ('move', 'move')], max_length=10)),
                ('state', architect.fields.JSONField(default={}, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('nonce', models.CharField(unique=True, max_length=26)),
                ('state', models.CharField(choices=[('new', 'new'), ('built', 'built'), ('destroyed', 'destroyed'), ('processing', 'processing')], max_length=10)),
                ('hostname', models.CharField(unique=True, max_length=200)),
                ('foundation_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('structure_id', models.IntegerField(blank=True, null=True, unique=True)),
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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('target', models.CharField(choices=[('foundation', 'foundation'), ('structure', 'structure')], max_length=10)),
                ('task', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('move', 'move')], max_length=7)),
                ('state', models.CharField(choices=[('new', 'new'), ('waiting', 'waiting'), ('done', 'done'), ('error', 'error')], max_length=7)),
                ('web_hook_token', models.CharField(blank=True, null=True, max_length=40)),
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
