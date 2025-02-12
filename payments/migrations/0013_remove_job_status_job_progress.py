# Generated by Django 4.0.8 on 2022-12-02 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0012_job_description_rendered_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='status',
        ),
        migrations.AddField(
            model_name='job',
            name='progress',
            field=models.CharField(choices=[('NEW', 'In Progress'), ('RVW', 'Reviewing'), ('OK', 'Completed')], default='NEW', help_text='The current status of the job', max_length=3),
        ),
    ]
