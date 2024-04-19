# Generated by Django 4.2.11 on 2024-04-10 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('buyproducts', '0002_product_variant_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='author_description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='is_active',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AlterField(
            model_name='multipleimages',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buyproducts.product_variant'),
        ),
    ]