# Generated by Django 5.0.3 on 2024-04-24 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newapp', '0014_appointment_is_generated_invoice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='payment_status',
            field=models.CharField(default='Not paid', max_length=50),
        ),
    ]
