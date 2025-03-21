# Generated by Django 5.1 on 2025-01-23 06:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0061_offer_description_offer_title_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='discount_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='discount_percentage',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='offer',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='myapp.service'),
        ),
    ]
