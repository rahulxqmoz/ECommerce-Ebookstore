from django.shortcuts import render,redirect

from user_app.models import CustomUser
from buyproducts.models import Product_variant, Wishlist
from django.contrib import messages
from django.db.models import Sum,F,Q
# Create your views here.

def add_wish_list(request,id):
    try:
        if 'user' in request.session:
            my_user = request.user
        else:
            messages.error(request,'You need to login to add to wishlist!')
            return redirect('user_login')    
        product=Product_variant.objects.get(id=id)
        user=CustomUser.objects.get(id=request.user.id)
        print(product)
        if product:
            wishlist=Wishlist.objects.filter(Q(product=product) & Q(user=user))
            if wishlist:
                messages.error(request,'product already in the list!')
                return redirect('product_detail',id=product.id)
            else:
                wish=Wishlist()
                wish.user=my_user
                wish.product=product
                wish.save()
                wishcount = wishlist=Wishlist.objects.filter(user=my_user).count()
                request.session['wishlishcount']=wishcount
                messages.success(request,'product added to wishlist!!')
                return redirect('product_detail',id=product.id)

    except Exception as e:
        print(e)
        messages.error(request,'add to wish failed!')
        return redirect('product_detail',id=product.id)           

    
def view_wishlist(request):
    context={}
    try:
        if 'user' in request.session:
            my_user = request.user
        else:
            messages.error(request,'You need to login to add to wishlist!')
            return redirect('user_login')    
        wishlist=Wishlist.objects.filter(user=my_user)
        if wishlist:
            context={'wishlist':wishlist}
        else:    
            messages.error(request,'No products in wishlist!!')
            return redirect('index')     
    except Exception as e:
        messages.error(request,'Error!!Page Not found!!')
        return redirect('index')    
    return render(request,'products/wishlist.html',context)


def delete_wish_list(request,id):
    try:
        if 'user' in request.session:
            my_user = request.user
        else:
            messages.error(request,'You need to login to add to wishlist!')
            return redirect('user_login')    
        product=Product_variant.objects.get(id=id)
        if product:
            wishlist=Wishlist.objects.filter(Q(product=product) & Q(user=my_user))
            if wishlist.exists():
                wishlist.delete()
                wishcount = wishlist=Wishlist.objects.filter(user=my_user).count()
                request.session['wishlishcount']=wishcount
                messages.success(request,'you have removed the product from wishlist!!')
                return redirect('view_wishlist')
    
            else:
                
                messages.error(request,'Removed Failed/Product not found in wishlist!!')
                return redirect('view_wishlist')

    except Exception as e:
        print(e)
        messages.error(request,'add to wish failed!')
        return redirect('product_detail',id=product.id)  