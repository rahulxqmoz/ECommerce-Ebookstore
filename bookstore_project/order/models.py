from django.db import models
from user_app.models import *
from cart.models import *
from buyproducts.models import Product_variant
# Create your models here.

class Payments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=100)
    total_amount = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_id
    
class OrderAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True)
    alternative_mobile = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, null=True)
    town = models.CharField(max_length=150, null=False)
    zip_code = models.IntegerField(null=False)
    nearby_location = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=150, null=False)
    state = models.CharField(max_length=150, null=False)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}"    

class Order(models.Model):
    STATUS = {
        ('Order confirmed', 'Order confirmed'),
        ('Shipped', 'Shipped'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Return requested', 'Return requested'),
        ('Return processing', 'Return processing'),
        ('Returned', 'Returned'),
    }
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=200, blank=True)
    order_address=models.ForeignKey(OrderAddress, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.FloatField(blank=True)
    order_total = models.FloatField()
    discount_amount = models.FloatField(default=0, blank=True)
    tax = models.FloatField()
    shipping_cost = models.FloatField(default=0)
    status = models.CharField(max_length=50, choices=STATUS, default="Order confirmed")
    is_ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_amount=models.FloatField(null=True)
    category_amount=models.FloatField(null=True)

    def __str__(self):
        return self.order_id

class OrderProduct(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payments, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product_variant, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    return_request = models.BooleanField(default=False)
    return_accept = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)
    return_reason = models.TextField(blank=True)
    item_cancel = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.customer.email} - {self.product.variant_name}"