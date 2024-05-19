# Generated by Django 5.0.4 on 2024-04-27 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0020_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Returned', 'Returned'), ('Shipped', 'Shipped'), ('Order confirmed', 'Order confirmed'), ('Cancelled', 'Cancelled'), ('Return requested', 'Return requested'), ('Return processing', 'Return processing'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered')], default='Order confirmed', max_length=50),
        ),
    ]