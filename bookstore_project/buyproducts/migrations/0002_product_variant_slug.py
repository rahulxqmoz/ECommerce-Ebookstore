# Generated by Django 5.0.4 on 2024-04-09 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyproducts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product_variant',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ]
