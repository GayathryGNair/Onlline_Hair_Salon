# Generated by Django 5.1 on 2024-09-24 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_client_employee_delete_booking_delete_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='reset_token',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='reset_token',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
