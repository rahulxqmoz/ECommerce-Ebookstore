from decimal import Decimal,ROUND_HALF_UP
from django.contrib import messages
from django.shortcuts import render,redirect
import pdb
from order.models import Order, OrderAddress
from user_app.models import CustomUser,UserAddress, WalletBook
from buyproducts.models import Product_variant
from . models import Cart,CartItem, Coupon
import uuid
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum,F,Q
import datetime
from order.models import Payments,OrderProduct
import razorpay
from django.conf import settings
# Create your views here.


def add_to_cart(request,id):
    try:
        if 'user' not in request.session:
            messages.error(request,'You need to login before adding to cart!')
            return redirect('user_login')
        else:
           
           
           product=Product_variant.objects.get(id=id)

           if product.stock <= 0:
               messages.error(request,'This book is out of stock!!!')
               return redirect('product_detail',id=id)

                        
            
           
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
                cartitem=CartItem.objects.filter(customer=user_obj).count()
                request.session['cart_item_count'] = cartitem
                return redirect('product_detail',id=id)
           if userexists.exists():
                productexits = CartItem.objects.filter(Q(product=product) & Q(customer=user_obj))
                if productexits.exists():
                    add_product=CartItem.objects.get(Q(product=product) & Q(customer=user_obj))
                  
                    if add_product.product.qty_per_person <= add_product.quantity:
                        messages.error(request,f'User cannot add more than {add_product.product.qty_per_person} quantity to the cart!!!')
                        return redirect('product_detail',id=id)
                    elif add_product.product.stock <= add_product.quantity:
                        messages.error(request,f'Item stock exhausted!!!')
                        return redirect('product_detail',id=id)

                    else:    
                        add_product.quantity=add_product.quantity+1
                        add_product.save()
                    messages.success(request,'Successfully add one more quantity to cart!')
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
            coupons=Coupon.objects.filter(is_active=True).order_by('-id')
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)
            context={'cartitem':cartItem,'coupons':coupons,'couponobj':cart_obj}
    except Exception as e:
        print(e)
        messages.error(request,'Your cart is empty!!')
        return redirect('index')        
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
    if 'user' not in request.session:
            messages.error(request,'You need to login before enetring to cart!')
            return redirect('user_login')
    try:
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
            if new_quantity!=0:
                if cart_item.product.stock <= 0:
                    return JsonResponse({'error': 'Item is out of stock!!Please try again later!!','hide_quantity': True})    
            if new_quantity!=0:
                if cart_item.product.stock < new_quantity:

                    return JsonResponse({'error': 'Item stock exceeded!!','hide_quantity': True})
                        
           
            # Update the quantity of the cart item
            if new_quantity!=0:
                cart_item.quantity = new_quantity
                if cart_item.product.qty_per_person < cart_item.quantity:
                    return JsonResponse({'error': f'User cannot add more than {cart_item.product.qty_per_person} quantity to the cart!!','hide_quantity':True})    
                cart_item.save()

            # Calculate new subtotal and grand total
            if new_quantity!=0:
                user=CustomUser.objects.get(id=request.user.id)
                cartitem = CartItem.objects.filter(customer=user)
            else:
                user=CustomUser.objects.get(id=request.user.id)
                cartitem = CartItem.objects.filter(customer=user)
            print('entered quanitty')
            sub_total=0   
            if new_quantity!=0:
                print('entered new quantity')

                if cart_item.product.offerprice() > 0 and cart_item.product.catoffer() > 0:
                    if cart_item.product.offerprice() < cart_item.product.catoffer():
                        sub_total=int(cart_item.product.offerprice()) * new_quantity
                    else:
                        sub_total=int(cart_item.product.catoffer()) * new_quantity
                elif cart_item.product.offerprice() > 0:
                    sub_total=int(cart_item.product.offerprice()) * new_quantity
                elif cart_item.product.catoffer() > 0:
                    sub_total=int(cart_item.product.catoffer()) * new_quantity 
                else:
                    sub_total=int(cart_item.product.product_price) * new_quantity     

                    

                # if cart_item.product.offer:
                #     if not cart_item.product.offer.is_expired():
                #         if cart_item.product.category.offer:
                #             if not cart_item.product.category.offer.is_expired():
                #                 if cart_item.product.offerprice() < cart_item.product.catoffer():
                #                     sub_total=int(cart_item.product.offerprice()) * new_quantity
                #                 else:
                #                     sub_total=int(cart_item.product.catoffer()) * new_quantity
                #             else:
                #                 sub_total=int(cart_item.product.offerprice()) * new_quantity
                                
                #         else:
                #             sub_total=int(cart_item.product.offerprice()) * new_quantity
                #     else:
                #         if cart_item.product.category.offer:
                #             if not cart_item.product.category.offer.is_expired():
                #                 sub_total=int(cart_item.product.catoffer()) * new_quantity
                #         else:
                #             sub_total=int(cart_item.product.product_price) * new_quantity  
                # else:
                #     print("entered else")
                #     if cart_item.product.category.offer:
                #         print("entered offer")
                #         if not cart_item.product.category.offer.is_expired():
                #             print("entered after expiry")
                #             sub_total=int(cart_item.product.catoffer()) * new_quantity
                #             print(sub_total)
                #         else:
                #             sub_total=int(cart_item.product.product_price) * new_quantity     
                #     else:
                #         sub_total=int(cart_item.product.product_price) * new_quantity  
            else:
                sub_total = sum(
                (
                    (
                        (int(item.product.offerprice()) if item.product.offerprice() < item.product.catoffer() else int(item.product.catoffer())) 
                        if (item.product.offerprice() is not None and item.product.catoffer() is not None and item.product.offerprice() > 0 and item.product.catoffer() > 0)
                        else (int(item.product.offerprice()) if item.product.offerprice() is not None and item.product.offerprice() > 0 else int(item.product.catoffer()) if item.product.catoffer() is not None and item.product.catoffer() > 0 else int(item.product.product_price))
                    )
                    if (item.product.offerprice() is not None and item.product.offerprice() > 0) or (item.product.catoffer() is not None and item.product.catoffer() > 0)
                    else int(item.product.product_price)
                ) * new_quantity 
                for item in cart_item
            )




                #sub_total=sum(int(item.product.offerprice()) * item.quantity for item in cart_item)    
                
            total_sub_total = cartitem.annotate(subtotal=F('product__product_price') * F('quantity'))
            total_sum = total_sub_total.aggregate(total_sum=Sum('subtotal'))
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id)
            total = sum(Decimal(item.sub_total()) for item in cart_item)
            # total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total=int(total)
            print('total')
            print(sub_total)
            print(total)
            print(total_sum['total_sum'])



            discount_amount=0
            tax=0
            couponcode=" "
            category_offeramount=0
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)

            #Calculate coupon amount and getting coupons
            alreadycouponexists=False
            if cart_obj.coupon:
                if cart_obj.coupon.is_expired():
                    return JsonResponse({'error': f'Coupon is expired!'})
                alreadycouponexists=True
                couponcode=f'Applied coupon code {cart_obj.coupon.coupon_code} successfully'
                if cart_obj.coupon.min_amount > total:
                    return JsonResponse({'error': f'Total product price should be greater than {cart_obj.coupon.min_amount}'})
                discount_amount = total * int(cart_obj.coupon.off_percent) / 100
                
                if discount_amount > cart_obj.coupon.max_discount:
                    discount_amount = cart_obj.coupon.max_discount
               
                if discount_amount > 0.7 * total:
                    discount_amount= 0.7 * total     
                
            #add coupons
            try:
                get_coupon = Coupon.objects.get(coupon_code=coupon_code)
                
            except Coupon.DoesNotExist:
                get_coupon = None
            if get_coupon:
                if get_coupon.is_expired():
                    return JsonResponse({'error': f'Coupon is expired!'})
                cart_obj.coupon=get_coupon
                if get_coupon.min_amount > total:
                    return JsonResponse({'error': f'Amount should be greater than {get_coupon.min_amount}'})
                discount_amount = total * int(get_coupon.off_percent) / 100
                if discount_amount > get_coupon.max_discount:
                    discount_amount = get_coupon.max_discount
                if discount_amount > 0.7 * total:
                    discount_amount= 0.7 * total 
                print(discount_amount) 
                print(0.7 * total)            
                cart_obj.save()
                couponcode=f'Applied coupon code {get_coupon.coupon_code} successfully'
                alreadycouponexists=True

            #Calculating Category offer
            # cat_ofr_obj = CartItem.objects.filter(cart=cart_obj)
            # print("cat expired")
            # for items in cat_ofr_obj:
            #     if not items.product.category.offer.is_expired():
            #         category_offeramount+=items.sub_total_with_category_offer()
            #     else:
            #         category_offeramount+=0    
            print("cat after")        
            #Calculating total amount 
            discount = total_sum['total_sum'] - total
            shipping=0
            if category_offeramount > 0 :
                total=total-category_offeramount
              
            
            total=total-discount_amount
            if total >0:
                tax = (total * 3) // 100 
                total=total+tax
            if total < 1000:
                shipping=99
                total=total+shipping
            else:
                shipping=0         
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)
            cart_obj.tax=tax
            cart_obj.save()
            return JsonResponse({'sub_total': sub_total, 'grand_total': total,'subtotaloffer':total_sum['total_sum'],'discount':discount,'shipping':shipping,'couponoffer':discount_amount,'tax':tax,'couponcode':couponcode,'alreadycouponexists':alreadycouponexists,'category_offeramount':category_offeramount})
    except Exception as e:
        print(e)
        messages.error(request,'Page exception found!!')
        return redirect('index')
    return JsonResponse({'error': 'Invalid request'}, status=400)


def checkout_address(request):
    try:
        if 'user' not in request.session:
            messages.error(request,'You need to login before enetring to cart!')
            return redirect('user_login')
        context={}
        user=CustomUser.objects.get(id=request.user.id)
        address=UserAddress.objects.filter(user=user)
        context={'address':address}
    except Exception as e:
        print(e)    

    return render(request,'products/checkout_address.html',context)

def place_order(request,id):
    try:
        context={}
        if 'user' not in request.session:
            messages.error(request,'You need to login before enetring to cart!')
            return redirect('user_login')
        add_id=id
        payments={}
        order_id=''
        order=''
        callback= "http://" + "ebookstores.xyz" + "/cart/place_order/{}".format(add_id)
        payment_method = request.GET.get('payment_method')
        razorpay_id=request.GET.get('razor_id')
        #useraddress=UserAddress.objects.get(id=id)
       
        user=CustomUser.objects.get(id=request.user.id)
        cartitem=CartItem.objects.filter(customer=user)
        cart_obj_get = CartItem.objects.filter(customer=user).first()
        cart_obj=Cart.objects.get(id=cart_obj_get.cart.id)
        if cart_obj.coupon:
            coupon_obj=Coupon.objects.get(id=cart_obj.coupon.id)
        else:
            coupon_obj=None    
        tax=0
        withoffer=0
        withoutoffer=0
        discount_amount=0
        shipping_cost=0
        coupon_discount=0
        category_offeramount=0

        

        #discount amount
        for cart in cartitem:
            withoffer += int(cart.sub_total())   
        for cart in cartitem:
            withoutoffer+= int(cart.product.product_price) * cart.quantity  
        discount_amount=withoutoffer-withoffer
        #coupon
        if cart_obj.coupon:
            coupon_discount=withoffer * int(cart_obj.coupon.off_percent)/100
            if withoffer<cart_obj.coupon.min_amount:
                messages.error(request,f'Minimum amount should be Rs.{cart_obj.coupon.min_amount}')
                return redirect('place_order')
            if cart_obj.coupon.max_discount<=coupon_discount:
                coupon_discount=cart_obj.coupon.max_discount
            if coupon_discount>0:
                withoffer=withoffer-coupon_discount  
        #Calculating Category offer
        # cat_ofr_obj = CartItem.objects.filter(cart=cart_obj)
        # for items in cat_ofr_obj:
        #     if not items.product.category.offer.is_expired():
        #         category_offeramount+=items.sub_total_with_category_offer()           
        #tax           
        tax=cart_obj.tax
        if tax>0:
            withoffer=withoffer+tax
        if  withoffer<1000:
            shipping_cost=99
            withoffer=withoffer+shipping_cost 
        if category_offeramount>0:
            withoffer=withoffer-category_offeramount
            
        #validating user address    
        try:
            useraddress = UserAddress.objects.get(id=id)
        except UserAddress.DoesNotExist:
            if payment_method == 'razorpay':
                user.wallet+=Decimal(withoffer)
                wallet = WalletBook.objects.create(
                customer=user,
                description="Amount received due to the failure of order!",
                increment=True,
                amount=str(withoffer)
                )
                user.save()
                messages.error(request, f'Unfortunatelly your order has been failed!!.Your amount Rs. {withoffer} will be credited to your wallet.Reason-User Address not found! Create a new one or select another address.')
                return redirect('checkout_address')
            messages.error(request, 'User Address not found! Create a new one or select another address.')
            return redirect('checkout_address')    
        context={
                'address':useraddress,
                 'cartitem':cartitem,
                 'withoffer':withoffer,
                 'withoutoffer':withoutoffer,
                 'discount_amount':discount_amount,
                 'coupon_amount':coupon_discount,
                 'tax':tax,
                 'shipping':shipping_cost,
                 'add_id':add_id,
                 'payment':payments,
                 'order_id':order_id,
                 'orders':order,
                 'callback_url':callback,
                 'category_offeramount':category_offeramount
                }    

        #checking stock
        for item in cartitem:
            if item.quantity>item.product.stock:
                messages.error(request,f'Only stock {item.product.stock} left for {item.product.variant_name}!Reduce Quantity from cart or Try Later!.')
                return redirect('place_order',context)    

        if request.method == "GET":
            # Check if payment failed
            payment_failed = request.GET.get('payment_failed', False)
            if payment_failed:
                error_code = request.GET.get('error_code')
                error_description = request.GET.get('error_description')
                # Handle the error message accordingly
                messages.error(request, f"Payment failed. Error code: {error_code}. Description: {error_description} !!")        
       
        #payment razorpay 
        if payment_method == 'razorpay':
                try:
                    useraddress = UserAddress.objects.get(id=id)
                except UserAddress.DoesNotExist:
                    user.wallet+=Decimal(withoffer)
                    wallet = WalletBook.objects.create(
                    customer=user,
                    description="Amount received due to the failure of order!",
                    increment=True,
                    amount=str(withoffer)
                    )
                    user.save()
                    messages.error(request, f'Unfortunatelly your order has been failed!!.Your amount Rs. {withoffer} will be credited to your wallet.Reason-User Address not found! Create a new one or select another address.')
                    return redirect('checkout_address')
                
                for item in cartitem:
                    try:
                        product_obj = Product_variant.objects.get(id=item.product.id,is_active=False)
                        user.wallet+=Decimal(withoffer)
                        wallet = WalletBook.objects.create(
                        customer=user,
                        description="Amount received due to the failure of order!",
                        increment=True,
                        amount=str(withoffer)
                        )
                        user.save()
                      
                        messages.error(request,f'Apologies!!Unfortunatelly your order has been failed!!.Your amount Rs. {withoffer} will be credited to your wallet.Reason :- {product_obj.variant_name} is not available for sale now.Try again Later!!.')
                        return redirect('place_order',context)
                    except Product_variant.DoesNotExist:
                        pass 
                my_order = Order()
                my_order.user = user
                my_order.address = useraddress
                order_address = OrderAddress.objects.create(
                    user=useraddress.user,
                    name=useraddress.name,
                    alternative_mobile=useraddress.alternative_mobile,
                    address=useraddress.address,
                    nearby_location=useraddress.nearby_location,
                    town=useraddress.town,
                    zip_code=useraddress.zip_code,
                    district=useraddress.district,
                    state=useraddress.state
                )
                my_order.order_address=order_address
                my_order.subtotal = withoutoffer
                my_order.order_total = withoffer  # product's total amount.
                my_order.discount_amount = discount_amount
                my_order.tax = tax
                my_order.category_amount=category_offeramount
                my_order.is_ordered = True
                if coupon_obj:
                    my_order.coupon = coupon_obj
                else:
                    my_order.coupon=None    
                my_order.coupon_amount=coupon_discount
                my_order.shipping_cost=shipping_cost
                paymentMethod=request.POST.get('payment')  
                my_order.save()
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_id = current_date + str(my_order.id)  # creating order id
                my_order.order_id = order_id

                my_order.save()

                # creating object for payment.
                payment = Payments.objects.create(
                    user=user,
                    total_amount=withoffer,
                    is_paid=False,
                ) 

                # creating order items
                for item in cartitem:
                    product_obj = Product_variant.objects.get(id=item.product.id)
                    productprice=product_obj.price_sub_total()
                    order_item = OrderProduct.objects.create(
                        customer=user,
                        order_id=my_order,
                        payment_id=payment.id,
                        product=product_obj,
                        quantity=item.quantity,
                        product_price=productprice,
                        ordered=True,
                    )
                    product_obj.stock = product_obj.stock - item.quantity
                    product_obj.save()
                    item.delete()
                try:
                    cartitem.delete()
                except:
                    pass
                if razorpay_id:
                    payment.payment_method = 'Razor Pay'  # set current payment method
                    payment.payment_id = razorpay_id  # check this payment_id
                    payment.is_paid = True
                    payment.save()
                    my_order.payment = payment
                    my_order.save()
                    user_id=CustomUser.objects.get(id=request.user.id)
                    cartitem=CartItem.objects.filter(customer=user_id).count()
                    request.session['cart_item_count'] = cartitem
                    return render(request, 'products/confirm_order.html')
        if request.method=="POST":
            paymentMethod=request.POST.get('payment')
            if paymentMethod is not None and paymentMethod.strip() != '':

                try:
                    useraddress = UserAddress.objects.get(id=id)
                except UserAddress.DoesNotExist:
                    messages.error(request, 'User Address not found! Create a new one or select another address.')
                    return redirect('checkout_address')
                
                for item in cartitem:
                    try:
                        product_obj = Product_variant.objects.get(id=item.product.id,is_active=False)
                        messages.error(request,f'Apologies!!{product_obj.variant_name} is not available for sale now.Try again Later!!.')
                        return redirect('place_order',context)
                    except Product_variant.DoesNotExist:
                        pass 

                if paymentMethod == "cod":
                    if withoffer > 1000:
                        messages.error(request,'Order above Rs.1000 is not allowed for Cash On Delivery.Use other payments options!')
                        return redirect('place_order',id=id) 
                    
                if paymentMethod=="wallet":
                    if withoffer > user.wallet:
                        messages.error(request,'No sufficient balance in your wallet to make this order!')
                        return redirect('place_order',id=id) 

                my_order = Order()
                my_order.user = user
                my_order.address = useraddress
                order_address = OrderAddress.objects.create(
                    user=useraddress.user,
                    name=useraddress.name,
                    alternative_mobile=useraddress.alternative_mobile,
                    address=useraddress.address,
                    nearby_location=useraddress.nearby_location,
                    town=useraddress.town,
                    zip_code=useraddress.zip_code,
                    district=useraddress.district,
                    state=useraddress.state
                )
                my_order.order_address=order_address
                my_order.subtotal = withoutoffer
                my_order.order_total = withoffer  # product's total amount.
                my_order.discount_amount = discount_amount
                my_order.tax = tax
                my_order.category_amount=category_offeramount
                my_order.is_ordered = True
                if coupon_obj:
                    my_order.coupon = coupon_obj
                else:
                    my_order.coupon=None    
                my_order.coupon_amount=coupon_discount
                my_order.shipping_cost=shipping_cost
                paymentMethod=request.POST.get('payment')  
                my_order.save()
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_id = current_date + str(my_order.id)  # creating order id
                my_order.order_id = order_id

                my_order.save()

                # creating object for payment.
                payment = Payments.objects.create(
                    user=user,
                    total_amount=withoffer,
                    is_paid=False,
                ) 

                # creating order items
                for item in cartitem:
                    product_obj = Product_variant.objects.get(id=item.product.id)
                    productprice=product_obj.price_sub_total()
                    order_item = OrderProduct.objects.create(
                        customer=user,
                        order_id=my_order,
                        payment_id=payment.id,
                        product=product_obj,
                        quantity=item.quantity,
                        product_price=productprice,
                        ordered=True,
                    )
                    product_obj.stock = product_obj.stock - item.quantity
                    product_obj.save()
                    item.delete()
                try:
                    cartitem.delete()
                except:
                    pass
                #Cash on delivery code
                if paymentMethod == "cod":
                    payment.payment_method = 'Cashon Delivery'  # set current payment method
                    payment_id = order_id + "COD"
                    payment.payment_id = payment_id
                    payment.save()
                    my_order.payment = payment
                    my_order.save()
                    user_id=CustomUser.objects.get(id=request.user.id)
                    cartitem=CartItem.objects.filter(customer=user_id).count()
                    request.session['cart_item_count'] = cartitem
                    return render(request, 'products/confirm_order.html')
                #Wallet payment code
                if paymentMethod == "wallet":
                    wallet_amount=user.wallet
                    if wallet_amount>=withoffer:
                        payment.payment_method = 'Wallet'
                        payment_id = order_id + "WALLET"
                        payment.payment_id = payment_id
                        payment.is_paid = True
                        payment.save()
                        my_order.payment = payment
                        my_order.save()
                        user.wallet-=Decimal(withoffer)
                        user.save()
                        wallet_acc = WalletBook()
                        wallet_acc.customer = user
                        wallet_acc.amount = withoffer
                        wallet_acc.description = "Product purchased.Money deducted from wallet!!"
                        wallet_acc.increment = False
                        wallet_acc.save()
                        user_id=CustomUser.objects.get(id=request.user.id)
                        cartitem=CartItem.objects.filter(customer=user_id).count()
                        request.session['cart_item_count'] = cartitem
                        return render(request, 'products/confirm_order.html')
                    else:
                        messages.error(request,f'You wallet amount is to low for make a payment.Wallet Balance Rs.{wallet_amount}') 
                        return redirect('place_order',id=id)    
            else:
                messages.error(request,'You to select a payment!!')
                return redirect('place_order',id=id)        
        context={
                'address':useraddress,
                 'cartitem':cartitem,
                 'withoffer':withoffer,
                 'withoutoffer':withoutoffer,
                 'discount_amount':discount_amount,
                 'coupon_amount':coupon_discount,
                 'tax':tax,
                 'shipping':shipping_cost,
                 'add_id':add_id,
                 'payment':payments,
                 'order_id':order_id,
                 'orders':order,
                 'callback_url':callback,
                 'category_offeramount':category_offeramount
                }
    except Exception as e:
        print(e)    
    return render(request,'products/place_order.html',context)


def remove_coupon(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        try:
            # Remove the coupon from the cart
            user_id = request.user.id
            cart_item = CartItem.objects.filter(customer=user_id).first()
            cart_obj = Cart.objects.get(id=cart_item.cart.id)
            cart_obj.coupon = None
            cart_obj.save()

            # Return success response
            return JsonResponse({'success': True})
        except Exception as e:
            # Return error response if any exception occurs
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Return error response for invalid requests
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

@csrf_exempt
def callback(request):
    try:
        def verify_signature(response_data):
            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
            return client.utility.verify_payment_signature(response_data)

        if "razorpay_signature" in request.POST:
            payment_id = request.POST.get("razorpay_payment_id", "")
            my_order_id = request.GET.get("order_id") 
            order = Order.objects.get(id=my_order_id)
            order.payment.payment_id = payment_id
            order.save()
            if not verify_signature(request.POST):
                order.payment.is_paid =True 
                order.save()
                return render(request, "confirm_order.html")
    except Exception as e:
        print(e)        
        

