# Generated by Django 5.1 on 2024-10-21 10:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0042_delete_booking'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_date', models.DateField()),
                ('booking_time', models.TimeField()),
                ('additional_notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.client')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.service')),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.employee')),
            ],
        ),
    ]
