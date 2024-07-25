# Generated by Django 5.0.3 on 2024-04-24 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('newapp', '0010_remove_prescription_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='consultation_fee',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='consultation_rate',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='is_forwarded_to_specialist',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='is_prescribed',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='appointment',
        ),
        migrations.AddField(
            model_name='invoice',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='object_id',
            field=models.PositiveIntegerField(default=2),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField(null=True)),
                ('status', models.CharField(max_length=20)),
                ('appointment_type', models.CharField(max_length=100)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_forwarded_to_specialist', models.BooleanField(default=False)),
                ('is_prescribed', models.BooleanField(default=False)),
                ('consultation_rate', models.DecimalField(decimal_places=2, default=10.0, max_digits=10)),
                ('consultation_fee', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='consultations', to='newapp.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultations', to='newapp.patient')),
            ],
        ),
    ]
