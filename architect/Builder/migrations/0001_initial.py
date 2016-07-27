# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Plan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('hostname', models.CharField(max_length=100)),
                ('structure_id', models.IntegerField(unique=True)),
                ('offset', models.IntegerField()),
                ('requested_at', models.DateTimeField(null=True, blank=True)),
                ('built_at', models.DateTimeField(null=True, blank=True)),
                ('unrequested_at', models.DateTimeField(null=True, blank=True)),
                ('destroyed_at', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(null=True, to='Plan.Member', on_delete=django.db.models.deletion.SET_NULL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('job_id', models.IntegerField()),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('regenerate', 'regenerate')], default='none', max_length=20)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('instance', models.ForeignKey(to='Builder.Instance')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='instance',
            unique_together=set([('member', 'offset')]),
        ),
    ]
