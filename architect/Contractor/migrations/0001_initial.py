# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BluePrint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('contractor_id', models.CharField(blank=True, max_length=40, unique=True, null=True)),
                ('name', models.CharField(blank=True, max_length=50, unique=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Complex',
            fields=[
                ('name', models.CharField(primary_key=True, max_length=40, serialize=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(to='Project.Site')),
            ],
        ),
    ]
