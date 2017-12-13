# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Contractor', '0001_initial'),
        ('Plan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('target', models.CharField(choices=[('foundation', 'foundation'), ('structure', 'structure')], max_length=10)),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('move', 'move')], max_length=7)),
                ('started', models.DateTimeField()),
                ('completed', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('nonce', models.CharField(unique=True, max_length=26)),
                ('hostname', models.CharField(unique=True, max_length=200)),
                ('foundation_id', models.IntegerField(unique=True, blank=True, null=True)),
                ('structure_id', models.IntegerField(unique=True, blank=True, null=True)),
                ('foundation_built', models.BooleanField(default=False)),
                ('structure_built', models.BooleanField(default=False)),
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
                ('target', models.CharField(choices=[('foundation', 'foundation'), ('structure', 'structure')], max_length=10)),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('move', 'move')], max_length=7)),
                ('state', models.CharField(choices=[('new', 'new'), ('waiting', 'waiting'), ('done', 'done'), ('error', 'error')], max_length=7)),
                ('web_hook_token', models.CharField(blank=True, null=True, max_length=30)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('history_entry', models.OneToOneField(to='Builder.History')),
                ('instance', models.OneToOneField(to='Builder.Instance')),
            ],
        ),
        migrations.AddField(
            model_name='history',
            name='instance',
            field=models.ForeignKey(to='Builder.Instance'),
        ),
    ]
