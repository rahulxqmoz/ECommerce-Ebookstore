# Generated by Django 5.0.4 on 2024-04-27 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0030_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Returned', 'Returned'), ('Delivered', 'Delivered'), ('Shipped', 'Shipped'), ('Order confirmed', 'Order confirmed'), ('Return requested', 'Return requested'), ('Out for delivery', 'Out for delivery'), ('Return processing', 'Return processing'), ('Cancelled', 'Cancelled')], default='Order confirmed', max_length=50),
        ),
    ]
