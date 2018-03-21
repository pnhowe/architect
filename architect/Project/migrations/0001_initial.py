# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Plan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('type', models.CharField(max_length=13, choices=[('site', 'site'), ('address_block', 'address_block')])),
                ('action', models.CharField(max_length=13, choices=[('add', 'add'), ('remove', 'remove'), ('change', 'change')])),
                ('target_id', models.CharField(max_length=50, blank=True, null=True)),
                ('current_val', architect.fields.JSONField(blank=True, null=True)),
                ('target_val', architect.fields.JSONField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('site', models.ForeignKey(blank=True, null=True, to='Plan.Site', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='Loader',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
        ),
    ]
