# Generated by Django 3.2.9 on 2021-11-26 23:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arch', '0022_alter_problem_aops_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='puid',
            field=models.CharField(
                help_text='Unique problem identifier, as printed in OTIS handout.',
                max_length=24,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Only uppercase letters and digits appear in PUID's.",
                        regex='^[A-Z0-9]+$')
                ],
                verbose_name='PUID'),
        ),
    ]
