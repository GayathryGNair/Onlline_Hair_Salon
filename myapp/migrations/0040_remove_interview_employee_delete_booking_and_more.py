# Generated by Django 5.1 on 2024-10-20 01:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0039_servicecategory_specialization'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interview',
            name='employee',
        ),
        migrations.DeleteModel(
            name='Booking',
        ),
        migrations.DeleteModel(
            name='Interview',
        ),
    ]
