# Generated by Django 5.1 on 2024-10-24 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0043_booking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='is_on_leave',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='leave_end',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='leave_start',
        ),
        migrations.DeleteModel(
            name='EmployeeAvailability',
        ),
    ]