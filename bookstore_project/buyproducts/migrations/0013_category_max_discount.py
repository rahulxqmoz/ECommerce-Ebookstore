# Generated by Django 5.0.4 on 2024-04-28 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyproducts', '0012_category_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='max_discount',
            field=models.PositiveBigIntegerField(null=True),
        ),
    ]
