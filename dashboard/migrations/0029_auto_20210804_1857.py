# Generated by Django 3.2.5 on 2021-08-04 22:57

import rpg.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0028_alter_pset_next_unit_to_unlock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='achievementcode',
            name='earned',
        ),
        migrations.AlterField(
            model_name='achievementcode',
            name='image',
            field=models.FileField(
                blank=True,
                help_text='Image for the obtained badge',
                null=True,
                upload_to=rpg.models.achievement_image_file_name),
        ),
    ]
