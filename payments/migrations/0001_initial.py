# Generated by Django 4.0.6 on 2022-07-29 23:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('roster', '0084_alter_invoice_memo'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(help_text='Amount paid')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(help_text='The invoice this contributes towards', on_delete=django.db.models.deletion.CASCADE, to='roster.invoice')),
            ],
        ),
    ]