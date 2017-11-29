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
            name='Instance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('nonce', models.CharField(unique=True, max_length=22)),
                ('hostname', models.CharField(unique=True, max_length=200)),
                ('structure_id', models.IntegerField(unique=True, blank=True, null=True)),
                ('requested_at', models.DateTimeField(blank=True, null=True)),
                ('built_at', models.DateTimeField(blank=True, null=True)),
                ('unrequested_at', models.DateTimeField(blank=True, null=True)),
                ('destroyed_at', models.DateTimeField(blank=True, null=True)),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('job_id', models.IntegerField()),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('regenerate', 'regenerate')], max_length=20, default='none')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('instance', models.ForeignKey(to='Builder.Instance')),
            ],
        ),
    ]
