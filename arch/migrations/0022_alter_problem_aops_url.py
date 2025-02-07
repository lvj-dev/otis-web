# Generated by Django 3.2.6 on 2021-09-01 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arch', '0021_alter_problem_puid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='aops_url',
            field=models.URLField(
                blank=True,
                help_text='URL to problem on AoPS. Include HTTPS.',
                max_length=128,
                verbose_name='AoPS URL'),
        ),
    ]
