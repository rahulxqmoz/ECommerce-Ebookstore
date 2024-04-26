from django.contrib import messages
from django.shortcuts import render,redirect
import pdb
from order.models import Order
from user_app.models import CustomUser,UserAddress
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
            coupons=Coupon.objects.all().order_by('-id')
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)
            context={'cartitem':cartItem,'coupons':coupons,'couponobj':cart_obj}
    except Exception as e:
        print(e)
        messages.error(request,'You have not added any items to cart yet!')
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
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)
            alreadycouponexists=False
            if cart_obj.coupon:
                alreadycouponexists=True
                couponcode=f'Applied coupon code {cart_obj.coupon.coupon_code} successfully'
                if cart_obj.coupon.min_amount > total:
                    return JsonResponse({'error': f'Amount should be greater than {cart_obj.coupon.min_amount}'})
                
                discount_amount = total * int(cart_obj.coupon.off_percent) / 100
                if discount_amount > cart_obj.coupon.max_discount:
                    discount_amount = cart_obj.coupon.max_discount
                
            #add coupons
            try:
                get_coupon = Coupon.objects.get(coupon_code=coupon_code)
            except Coupon.DoesNotExist:
                get_coupon = None
            
            if get_coupon:
            
                cart_obj.coupon=get_coupon
                
                if get_coupon.min_amount > total:
                    return JsonResponse({'error': f'Amount should be greater than {get_coupon.min_amount}'})
                
                discount_amount = total * int(get_coupon.off_percent) / 100
                if discount_amount > get_coupon.max_discount:
                    discount_amount = get_coupon.max_discount
                
                cart_obj.save()
                
                couponcode=f'Applied coupon code {get_coupon.coupon_code} successfully'
                alreadycouponexists=True

            discount = total_sum['total_sum'] - total
            shipping=0
            if total < 1000:
                shipping=99
                total=total+shipping
            else:
                shipping=0     
                
            total=total-discount_amount
            if total >0:
                tax = (total * 3) // 100 
                total=total+tax
            user_id = CustomUser.objects.get(id=request.user.id)
            cart_item = CartItem.objects.filter(customer=user_id).first() 
            cart_obj=Cart.objects.get(id=cart_item.cart.id)
            cart_obj.tax=tax
            cart_obj.save()

            return JsonResponse({'sub_total': sub_total, 'grand_total': total,'subtotaloffer':total_sum['total_sum'],'discount':discount,'shipping':shipping,'couponoffer':discount_amount,'tax':tax,'couponcode':couponcode,'alreadycouponexists':alreadycouponexists})
    except Exception as e:
        print(e)
        messages.error(request,'Page exception found!!')
        return redirect('index')
    return JsonResponse({'error': 'Invalid request'}, status=400)


def qty_per_person(stock):
    if stock>0:
        result = stock / 5
        return result
    else:
        return 0


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
        callback= "http://" + "127.0.0.1:8000" + "/cart/place_order/{}".format(add_id)
        payment_method = request.GET.get('payment_method')
        razorpay_id=request.GET.get('razor_id')

        

        useraddress=UserAddress.objects.get(id=id)
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
        
        for cart in cartitem:
            withoffer += int(cart.sub_total())   
        for cart in cartitem:
            withoutoffer+= int(cart.product.product_price) * cart.quantity  
        discount_amount=withoutoffer-withoffer

        if cart_obj.coupon:
            coupon_discount=withoffer * int(cart_obj.coupon.off_percent)/100
            if withoffer<cart_obj.coupon.min_amount:
                messages.error(request,f'Minimum amount should be Rs.{cart_obj.coupon.min_amount}')
                return redirect('place_order')
            if cart_obj.coupon.max_discount<=coupon_discount:
                coupon_discount=cart_obj.coupon.max_discount
            if coupon_discount>0:
                withoffer=withoffer-coupon_discount        
        tax=cart_obj.tax
       
        if tax>0:
            withoffer=withoffer+tax
        if  withoffer<1000:
            shipping_cost=99
            withoffer=withoffer+shipping_cost  
       
       
        if payment_method == 'razorpay':
                print("Entered to method")
                my_order = Order()
                my_order.user = user
                my_order.address = useraddress
                my_order.subtotal = withoutoffer
                my_order.order_total = withoffer  # product's total amount.
                my_order.discount_amount = discount_amount
                my_order.tax = tax
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
                    order_item = OrderProduct.objects.create(
                        customer=user,
                        order_id=my_order,
                        payment_id=payment.id,
                        product=product_obj,
                        quantity=item.quantity,
                        product_price=item.product.product_price,
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
               
               
                
                my_order = Order()
                my_order.user = user
                my_order.address = useraddress
                my_order.subtotal = withoutoffer
                my_order.order_total = withoffer  # product's total amount.
                my_order.discount_amount = discount_amount
                my_order.tax = tax
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
                    order_item = OrderProduct.objects.create(
                        customer=user,
                        order_id=my_order,
                        payment_id=payment.id,
                        product=product_obj,
                        quantity=item.quantity,
                        product_price=item.product.product_price,
                        ordered=True,
                    )
                    product_obj.stock = product_obj.stock - item.quantity
                    product_obj.save()
                    item.delete()
                try:
                    cartitem.delete()
                except:
                    pass
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
                if paymentMethod == "razorpay":
                    print('entered razor pay')
                    # grand_total=int(withoffer)
                    # client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
                    # payments=client.order.create({'amount':grand_total*100,'currency':'INR','payment_capture':0})
                    # order_id = payments['id']
                    # payment.payment_method = 'Razor Pay'  # set current payment method
                    # payment.payment_id = order_id  # check this payment_id
                    # payment.is_paid = False
                    # payment.save()
                    # my_order.payment = payment
                    # my_order.save()
                    # return render(request, 'products/confirm_order.html')
            

            else:
                messages.error(request,'You to select a payment!!')
                return redirect('place_order',id=id)        

       

        context={'address':useraddress,
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
                 'callback_url':callback

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
    

def razorpay_gateway(request):
    grand_total = request.GET.get('grand_total')
    print("Grand Total:", grand_total)  
    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    print(client)
    paymentrazor=client.order.create({'amount':int(float((grand_total))),'currency':'INR','payment_capture':1})
    print(paymentrazor)
    if grand_total:
        
        return HttpResponse(f'Payment processed for grand total: {grand_total}')
    else:
        return HttpResponse('Error: Grand total not provided')
    

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
        

