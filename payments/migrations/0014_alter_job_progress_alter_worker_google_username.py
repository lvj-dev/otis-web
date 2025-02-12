# Generated by Django 4.0.8 on 2022-12-02 05:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0013_remove_job_status_job_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='progress',
            field=models.CharField(choices=[('NEW', 'In Progress'), ('SUB', 'Submitted'), ('OK', 'Completed')], default='NEW', help_text='The current status of the job', max_length=3),
        ),
        migrations.AlterField(
            model_name='worker',
            name='google_username',
            field=models.CharField(blank=True, help_text='For e.g. sharing with Google Drive, etc. Do not include @gmail.com or @google.com.', max_length=128, validators=[django.core.validators.RegexValidator("[-a-zA-Z0-9_'.]+")]),
        ),
    ]
