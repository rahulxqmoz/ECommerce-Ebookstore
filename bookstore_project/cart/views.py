from django.contrib import messages
from django.shortcuts import render,redirect

from user_app.models import CustomUser
from buyproducts.models import Product_variant
from . models import Cart,CartItem
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,F
# Create your views here.


def add_to_cart(request,id):
    try:
       
        if 'user' not in request.session:
            messages.error(request,'You need to login before adding to cart!')
            return redirect('user_login')
        else:
           
           
           product=Product_variant.objects.get(id=id)
           
           user=request.user
           user_obj=CustomUser.objects.get(id=user.id)
           print(user_obj)

           userexists = CartItem.objects.filter(customer=user_obj)

           
           if not userexists.exists():
              
                token = str(uuid.uuid4())
                cart_obj=Cart(cart_id=token)
                cart_obj.save()
                cart_item=CartItem(customer=user_obj,product=product,cart=cart_obj)
                cart_item.save()
                messages.success(request,'Successfully add to cart!')
                return redirect('product_detail',id=id)
           if userexists.exists():
                productexits = CartItem.objects.filter(product=product)
                if productexits.exists():
                    messages.error(request,'Product Already in cart!!!')
                    return redirect('product_detail',id=id)     

                cart_obj =  userexists.first().cart 
                cart_item=CartItem(customer=user_obj,product=product,cart=cart_obj)
                cart_item.save()
                messages.success(request,'Successfully add to cart!')
                user_id=CustomUser.objects.get(id=request.user.id)
                cartitem=CartItem.objects.filter(customer=user_id).count()
                request.session['cart_item_count'] = cartitem
                return redirect('product_detail',id=id)

    except Exception as e:
        print(e)
        messages.error(request,'Add to cart failed')
        return redirect('product_detail',id=id)        


def view_cart(request,id):
    try:
        if 'user' not in request.session:
            messages.error(request,'You need to login before enetring to cart!')
            return redirect('user_login')
        else:
            user_id=CustomUser.objects.get(id=id)
            cartItem=CartItem.objects.filter(customer=user_id)
            context={'cartitem':cartItem}
    except Exception as e:
        print(e)        
    return render(request,'products/cart.html',context)

def delete_cart(request,id):
    try:
        if 'user' not in request.session:
            messages.error(request,'You need to login before enetring to cart!')
            return redirect('user_login')
        else:
            cartItem=CartItem.objects.get(id=id)
            cartItem.delete()
            messages.success(request,"item deleted!!")
            user_id=CustomUser.objects.get(id=request.user.id)
            cartitem=CartItem.objects.filter(customer=user_id).count()
            request.session['cart_item_count'] = cartitem
            return redirect('view_cart',id=request.user.id)
    except Exception as e:
        print(e) 
        return redirect('view_cart',id=request.user.id)   

@csrf_exempt
def update_cart_quantity(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('new_quantity', 1))
        print(item_id)
        # Retrieve the cart item
        try:
            cart_item = CartItem.objects.get(id=item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Cart item not found'})
        if cart_item.product.stock < new_quantity:
            return JsonResponse({'error': 'Item stock exceeded!!','hide_quantity': True})

        # Update the quantity of the cart item
        cart_item.quantity = new_quantity
        cart_item.save()

        # Calculate new subtotal and grand total
        user=CustomUser.objects.get(id=request.user.id)
        cartitem = CartItem.objects.filter(customer=user)
        sub_total = int(cart_item.product.offerprice()) * new_quantity  
        #sub_total=cart_item.sub_total()
        total_sub_total = cartitem.annotate(subtotal=F('product__product_price') * F('quantity'))
        total_sum = total_sub_total.aggregate(total_sum=Sum('subtotal'))
        user_id = CustomUser.objects.get(id=request.user.id)
        cart_item = CartItem.objects.filter(customer=user_id)
        total = sum(int(item.product.offerprice()) * item.quantity for item in cart_item)
        discount = int(total_sum['total_sum']) - total
        shipping=0
        if total < 3000:
            shipping=49
            total=total+shipping
        else:
            shipping=0    


        
    
        
        # Return the updated subtotal and grand total 
        return JsonResponse({'sub_total': sub_total, 'grand_total': total,'subtotaloffer':total_sum['total_sum'],'discount':discount,'shipping':shipping})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def qty_per_person(stock):
    if stock>0:
        result = stock / 5
        return result
    else:
        return 0

    