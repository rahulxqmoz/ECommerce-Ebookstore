from django.contrib import messages
from django.shortcuts import render,redirect
import pdb
from user_app.models import CustomUser
from buyproducts.models import Product_variant
from . models import Cart,CartItem, Coupon
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
            coupons=Coupon.objects.all().order_by('-id')
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)
            context={'cartitem':cartItem,'coupons':coupons,'couponobj':cart_obj}
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
        item_id_str = request.POST.get('item_id')
        new_quantity_str = request.POST.get('new_quantity')
        coupon_code=request.POST.get('coupon_code')
      
        

        try:
            new_quantity = int(new_quantity_str) if new_quantity_str.isdigit() else 0
        except ValueError:
            new_quantity = 0
        # Retrieve the cart item
    
        if item_id_str.isdigit():
            item_id = int(item_id_str)
           
            cart_item = CartItem.objects.get(id=item_id)
          
        else:
    
            user = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user)
            
            
        # try:
        #     cart_item = CartItem.objects.get(id=item_id)
        # except CartItem.DoesNotExist:
        #     return JsonResponse({'error': 'Cart item not found'})
        if new_quantity!=0:
            if cart_item.product.stock < new_quantity:
                return JsonResponse({'error': 'Item stock exceeded!!','hide_quantity': True})

        # Update the quantity of the cart item
        if new_quantity!=0:
            cart_item.quantity = new_quantity
            cart_item.save()

        # Calculate new subtotal and grand total
        if new_quantity!=0:
            user=CustomUser.objects.get(id=request.user.id)
            cartitem = CartItem.objects.filter(customer=user)
        else:
            user=CustomUser.objects.get(id=request.user.id)
            cartitem = CartItem.objects.filter(customer=user)   
        if new_quantity!=0:
            sub_total = int(cart_item.product.offerprice()) * new_quantity
        else:
            sub_total=sum(int(item.product.offerprice()) * item.quantity for item in cart_item)    
            
        #sub_total=cart_item.sub_total()
        total_sub_total = cartitem.annotate(subtotal=F('product__product_price') * F('quantity'))
        total_sum = total_sub_total.aggregate(total_sum=Sum('subtotal'))
        user_id = CustomUser.objects.get(id=request.user.id)
        cart_item = CartItem.objects.filter(customer=user_id)
        total = sum(int(item.product.offerprice()) * item.quantity for item in cart_item)
        
        
               

        discount_amount=0
        tax=0
        couponcode=" "
        #add coupons
        try:
            get_coupon = Coupon.objects.get(coupon_code=coupon_code)
        except Coupon.DoesNotExist:
            get_coupon = None
        
        if get_coupon:
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)
            cart_obj.coupon=get_coupon
            
            if get_coupon.min_amount > total:
                return JsonResponse({'error': f'Amount should be greater than {get_coupon.min_amount}'})
            
            discount_amount = total * int(get_coupon.off_percent) / 100
            if discount_amount > get_coupon.max_discount:
                discount_amount = get_coupon.max_discount
            
            
            cart_obj.save()
            couponcode=get_coupon.coupon_code

        discount = total_sum['total_sum'] - total
        shipping=0
        if total < 3000:
            shipping=99
            total=total+shipping
        else:
            shipping=0     
               
        total=total-discount_amount
        tax = (total * 3) // 100 
        total=total+tax
        user_id = CustomUser.objects.get(id=request.user.id)
        cart_item = CartItem.objects.filter(customer=user_id).first() 
        cart_obj=Cart.objects.get(id=cart_item.cart.id)
        cart_obj.tax=tax
        cart_obj.save()
        
         
        return JsonResponse({'sub_total': sub_total, 'grand_total': total,'subtotaloffer':total_sum['total_sum'],'discount':discount,'shipping':shipping,'couponoffer':discount_amount,'tax':tax,'couponcode':couponcode})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def qty_per_person(stock):
    if stock>0:
        result = stock / 5
        return result
    else:
        return 0

    