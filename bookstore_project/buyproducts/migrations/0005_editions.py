# Generated by Django 4.2.11 on 2024-04-11 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyproducts', '0004_offer_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Editions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('editons_name', models.CharField(max_length=150)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('Edition_description', models.TextField(null=True)),
                ('is_active', models.BooleanField(blank=True, default=True)),
            ],
        ),
    ]
