# Generated by Django 4.0.8 on 2022-11-24 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_jobfolder_worker_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='notes',
            field=models.TextField(blank=True, help_text='Any notes on payment or whatever.'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='paypal_username',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='worker',
            name='venmo_handle',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='worker',
            name='zelle_info',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
