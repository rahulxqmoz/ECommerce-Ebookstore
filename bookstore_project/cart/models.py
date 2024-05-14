from datetime import date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from user_app.models import CustomUser
from buyproducts.models import Product_variant,Products

# Create your models here.

def validate_expiry_date(value):
    min_date = date.today()
    if value < min_date:
        raise ValidationError(
            (f"Expiry date cannot be earlier than {min_date}.")
        )



class Coupon(models.Model):
    coupon_code = models.CharField(max_length=15)
    min_amount = models.PositiveBigIntegerField()
    off_percent = models.PositiveBigIntegerField()
    max_discount = models.PositiveBigIntegerField()
    coupon_stock = models.PositiveIntegerField(null=True, blank=True)
    expiry_date = models.DateField(validators=[validate_expiry_date])
    is_active=models.BooleanField(default=True,null=False, blank=True)

    def __str__(self):
        return self.coupon_code
    
    def is_expired(self):
        if self.coupon_stock == 0 or self.expiry_date < date.today():
            return True
        return False
    
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)  
    date_added = models.DateField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.FloatField(null=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product_variant, on_delete=models.SET_NULL, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True)

    

    class Meta:
        ordering = ['created_date']

    def sub_total(self):
        if self.product.offerprice() > 0 and self.product.catoffer() > 0:
            minproduct_price= min(self.product.offerprice(),self.product.catoffer())
            return minproduct_price * self.quantity
        elif self.product.offerprice() > 0:
            return self.product.offerprice() * self.quantity
        elif self.product.catoffer() > 0:
            return self.product.catoffer() * self.quantity
        
        else:
            return self.product.product_price * self.quantity


        
    
    def sub_total_without_offer(self):
        return self.product.price * self.quantity
    
    def sub_total_with_category_offer(self):
        result = int((self.sub_total()) - (self.sub_total() * self.product.category.offer.off_percent)/100 )
        if result > self.product.category.max_discount:
            if self.product.category.max_discount is not None: 
                result=self.product.category.max_discount
        return result

    def __str__(self):
        return f"self.product.variant_name"


