# Generated by Django 5.0.4 on 2024-04-16 16:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0007_delete_userreview'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150)),
                ('alternative_mobile', models.CharField(blank=True, max_length=10, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('town', models.CharField(max_length=150)),
                ('zip_code', models.IntegerField()),
                ('nearby_location', models.CharField(blank=True, max_length=255)),
                ('district', models.CharField(max_length=150)),
                ('state', models.CharField(max_length=150)),
                ('created', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
