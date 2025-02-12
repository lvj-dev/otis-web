# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-19 20:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0011_auto_20170813_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='legit',
            field=models.BooleanField(
                default=True,
                help_text=
                'Whether this student is real. Set to false for dummy accounts and the like. This will hide them from the master schedule, for example.'
            ),
        ),
    ]
