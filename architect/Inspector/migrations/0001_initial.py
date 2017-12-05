# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import architect.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Builder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('instance', models.OneToOneField(primary_key=True, serialize=False, to='Builder.Instance')),
                ('state', architect.fields.JSONField()),
                ('target_count', models.IntegerField(default=0)),
                ('next_check', models.DateTimeField()),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
