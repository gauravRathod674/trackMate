# Generated by Django 4.2.8 on 2024-01-04 08:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackmate', '0011_alter_product_image_alter_product_no_of_ratings_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='source',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='budget',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
