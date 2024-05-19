# Generated by Django 5.0.4 on 2024-04-27 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0028_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Shipped', 'Shipped'), ('Return requested', 'Return requested'), ('Return processing', 'Return processing'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Out for delivery', 'Out for delivery'), ('Order confirmed', 'Order confirmed'), ('Delivered', 'Delivered')], default='Order confirmed', max_length=50),
        ),
    ]