# Generated by Django 5.1 on 2025-01-22 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0059_remove_offer_description_remove_offer_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
