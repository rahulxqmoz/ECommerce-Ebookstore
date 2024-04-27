# Generated by Django 5.0.4 on 2024-04-27 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0025_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Delivered', 'Delivered'), ('Return requested', 'Return requested'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Shipped', 'Shipped'), ('Return processing', 'Return processing'), ('Order confirmed', 'Order confirmed'), ('Out for delivery', 'Out for delivery')], default='Order confirmed', max_length=50),
        ),
    ]
