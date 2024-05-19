# Generated by Django 5.0.4 on 2024-04-27 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Return requested', 'Return requested'), ('Shipped', 'Shipped'), ('Out for delivery', 'Out for delivery'), ('Order confirmed', 'Order confirmed'), ('Delivered', 'Delivered'), ('Returned', 'Returned'), ('Return processing', 'Return processing'), ('Cancelled', 'Cancelled')], default='Order confirmed', max_length=50),
        ),
    ]