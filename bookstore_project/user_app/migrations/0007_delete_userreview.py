# Generated by Django 4.2.11 on 2024-04-12 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0006_userreview'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserReview',
        ),
    ]