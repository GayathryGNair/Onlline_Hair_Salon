# Generated by Django 5.1 on 2024-10-18 10:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0038_specialization_remove_employee_specialization_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='specialization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_categories', to='myapp.specialization'),
        ),
    ]