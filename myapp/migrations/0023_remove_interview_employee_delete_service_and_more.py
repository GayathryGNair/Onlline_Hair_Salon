# Generated by Django 5.1 on 2024-10-12 02:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_interview'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interview',
            name='employee',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.DeleteModel(
            name='Interview',
        ),
    ]
