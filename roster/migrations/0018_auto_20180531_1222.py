# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-31 17:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0017_auto_20180531_1217'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ('semester', '-legit', 'track', 'name')},
        ),
        migrations.RenameField(
            model_name='student',
            old_name='classification',
            new_name='track',
        ),
    ]