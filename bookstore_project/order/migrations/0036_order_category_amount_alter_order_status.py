# Generated by Django 5.0.4 on 2024-04-28 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0035_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='category_amount',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Return requested', 'Return requested'), ('Return processing', 'Return processing'), ('Out for delivery', 'Out for delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Shipped', 'Shipped'), ('Order confirmed', 'Order confirmed'), ('Returned', 'Returned')], default='Order confirmed', max_length=50),
        ),
    ]
