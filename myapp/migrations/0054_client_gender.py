# Generated by Django 5.1 on 2025-01-10 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0053_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1, null=True),
        ),
    ]
