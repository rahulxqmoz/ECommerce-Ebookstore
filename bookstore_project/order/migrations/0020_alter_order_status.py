# Generated by Django 5.0.4 on 2024-04-27 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0019_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Shipped', 'Shipped'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'), ('Returned', 'Returned'), ('Order confirmed', 'Order confirmed'), ('Return requested', 'Return requested'), ('Cancelled', 'Cancelled'), ('Return processing', 'Return processing')], default='Order confirmed', max_length=50),
        ),
    ]
