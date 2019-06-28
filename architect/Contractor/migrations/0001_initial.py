# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrint',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('contractor_id', models.CharField(null=True, max_length=40, blank=True, unique=True)),
                ('name', models.CharField(null=True, max_length=50, blank=True, unique=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('name', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(to='Project.Site', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
    ]
