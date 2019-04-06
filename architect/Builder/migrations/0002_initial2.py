# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Contractor', '0001_initial'),
        ('Builder', '0001_initial'),
        ('Plan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='blueprint',
            field=models.ForeignKey(to='Plan.PlanBluePrint', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='instance',
            name='complex',
            field=models.ForeignKey(to='Contractor.Complex', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='instance',
            name='plan',
            field=models.ForeignKey(to='Plan.Plan', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='action',
            name='instance',
            field=models.OneToOneField(to='Builder.Instance', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
