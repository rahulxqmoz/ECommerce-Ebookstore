# Generated by Django 5.0.4 on 2024-04-27 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0026_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Shipped', 'Shipped'), ('Returned', 'Returned'), ('Delivered', 'Delivered'), ('Out for delivery', 'Out for delivery'), ('Return requested', 'Return requested'), ('Return processing', 'Return processing'), ('Order confirmed', 'Order confirmed'), ('Cancelled', 'Cancelled')], default='Order confirmed', max_length=50),
        ),
    ]
