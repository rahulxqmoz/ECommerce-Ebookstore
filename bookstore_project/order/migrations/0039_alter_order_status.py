# Generated by Django 5.0.4 on 2024-05-01 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0038_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Return requested', 'Return requested'), ('Returned', 'Returned'), ('Delivered', 'Delivered'), ('Shipped', 'Shipped'), ('Cancelled', 'Cancelled'), ('Order confirmed', 'Order confirmed'), ('Return processing', 'Return processing'), ('Out for delivery', 'Out for delivery')], default='Order confirmed', max_length=50),
        ),
    ]
