# Generated by Django 4.0.8 on 2022-11-21 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arch', '0026_alter_problem_puid'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='hyperlink',
            field=models.URLField(blank=True, help_text='An AoPS URL or similar'),
        ),
    ]