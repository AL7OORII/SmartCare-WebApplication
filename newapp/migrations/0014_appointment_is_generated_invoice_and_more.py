# Generated by Django 5.0.3 on 2024-04-24 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newapp', '0013_remove_prescription_appointment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='is_generated_invoice',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consultation',
            name='is_generated_invoice',
            field=models.BooleanField(default=False),
        ),
    ]
