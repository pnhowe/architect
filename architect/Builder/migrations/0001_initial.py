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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('hostname', models.CharField(max_length=100)),
                ('structure_id', models.IntegerField(unique=True)),
                ('offset', models.IntegerField()),
                ('requested_at', models.DateTimeField(blank=True, null=True)),
                ('built_at', models.DateTimeField(blank=True, null=True)),
                ('unrequested_at', models.DateTimeField(blank=True, null=True)),
                ('destroyed_at', models.DateTimeField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(blank=True, null=True, to='Plan.Member', on_delete=django.db.models.deletion.SET_NULL)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
