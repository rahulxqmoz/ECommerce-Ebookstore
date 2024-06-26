# Generated by Django 5.0.4 on 2024-04-21 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Order confirmed', 'Order confirmed'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'), ('Shipped', 'Shipped'), ('Returned', 'Returned'), ('Return processing', 'Return processing'), ('Cancelled', 'Cancelled'), ('Return requested', 'Return requested')], default='Order confirmed', max_length=50),
        ),
    ]
