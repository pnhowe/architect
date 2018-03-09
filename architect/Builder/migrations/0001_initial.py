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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('action', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('rebuild', 'rebuild'), ('move', 'move')], max_length=10)),
                ('state', architect.fields.JSONField(blank=True, default={})),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('state', models.CharField(choices=[('new', 'new'), ('built', 'built'), ('destroyed', 'destroyed'), ('processing', 'processing')], max_length=10)),
                ('hostname', models.CharField(unique=True, max_length=200)),
                ('foundation_id', models.IntegerField(blank=True, unique=True, null=True)),
                ('structure_id', models.IntegerField(blank=True, unique=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('target', models.CharField(choices=[('foundation', 'foundation'), ('structure', 'structure')], max_length=10)),
                ('task', models.CharField(choices=[('build', 'build'), ('destroy', 'destroy'), ('move', 'move')], max_length=7)),
                ('state', models.CharField(choices=[('new', 'new'), ('waiting', 'waiting'), ('done', 'done'), ('error', 'error')], max_length=7)),
                ('web_hook_token', models.CharField(blank=True, null=True, max_length=40)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='Builder.Action')),
            ],
        ),
        migrations.CreateModel(
            name='ComplexInstance',
            fields=[
                ('instance_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='Builder.Instance')),
                ('nonce', models.CharField(unique=True, max_length=26)),
                ('complex', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.Complex')),
            ],
            bases=('Builder.instance',),
        ),
        migrations.CreateModel(
            name='TypedInstance',
            fields=[
                ('instance_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='Builder.Instance')),
                ('site_id', models.CharField(max_length=40)),
                ('foundation_type', models.CharField(max_length=50)),
                ('address_block_id', models.IntegerField()),
                ('address_offset', models.IntegerField()),
            ],
            bases=('Builder.instance',),
        ),
        migrations.AddField(
            model_name='instance',
            name='blueprint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Contractor.BluePrint'),
        ),
        migrations.AddField(
            model_name='instance',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Plan.Plan'),
        ),
        migrations.AddField(
            model_name='action',
            name='instance',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='Builder.Instance'),
        ),
    ]
