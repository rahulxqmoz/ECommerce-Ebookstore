from django.db import models
from django.forms import ValidationError

from user_app.models import CustomUser
from datetime import date
# Create your models here.
def validate_expiry_date(value):
    min_date = date.today()
    if value < min_date:
        raise ValidationError(
            (f"Expiry date cannot be earlier than {min_date}.")
        )
    

class Category(models.Model):
    category_name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category_description = models.TextField(null=True)
    category_image = models.ImageField(upload_to='category_images/')
    is_active = models.BooleanField(default=True, null=False, blank=True)

    class Meta:
        ordering = ['category_name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def _str_(self):
        return '{}'.format(self.category_name)    
    


class Author(models.Model):
    author_name=models.CharField(max_length=150)
    slug=models.SlugField(max_length=100,unique=True,blank=True)
    author_image=models.ImageField(upload_to='author_images/')
    author_description=models.TextField()
    is_active=models.BooleanField(default=True)

def _str_(self):
        return self.author_name

     
class Products(models.Model):
    product_title=models.CharField(max_length=150)   
    slug=models.SlugField(max_length=100,unique=True,blank=True)
    product_image=models.ImageField(upload_to='product_images/')
    product_description=models.TextField()
    is_active=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now_add=True)

class Offer(models.Model):
    name = models.CharField(max_length=100)
    off_percent = models.PositiveBigIntegerField()
    start_date = models.DateField(validators=[validate_expiry_date])
    end_date = models.DateField()

    def __str__(self) -> str:
        return self.name
    
    def is_expired(self):
        print("date :::::::::::", date.today())
        if self.end_date < date.today():
            return True
        return False
    

class Product_variant(models.Model):
    variant_name=models.CharField(max_length=100,blank=True)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=True)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    author=models.ForeignKey(Author,on_delete=models.SET_NULL,null=True)
    product_price=models.DecimalField(max_digits=10,decimal_places=2)
    stock=models.IntegerField()
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
    offer=models.ForeignKey(Offer,on_delete=models.SET_NULL,null=True)
    rating=models.IntegerField()


class MultipleImages(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    images = models.ImageField(upload_to='multiple_images/', blank=True)

    def _str_(self):
        return self.product.product_name
    
class ProductReview(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(default=0)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)