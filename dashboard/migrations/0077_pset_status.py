# Generated by Django 4.0.7 on 2022-09-26 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0076_alter_pset_upload'),
    ]

    operations = [
        migrations.AddField(
            model_name='pset',
            name='status',
            field=models.CharField(choices=[('A', 'Accepted'), ('R', 'Rejected'), ('PA', 'Pending (prev accepted)'), ('PR', 'Pending (prev rejected)'), ('P', 'Pending (new)')], default='P', max_length=4),
        ),
    ]
