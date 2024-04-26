from django.shortcuts import render,redirect
import pdb

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from buyproducts.models import Product_variant
from order.models import OrderProduct,Order
# Create your views here.
@login_required(login_url='user_login')
def cancel_order(request,id):

    order_product = OrderProduct.objects.get(id=id)
    variant = Product_variant.objects.get(id=order_product.product.id)
    order_obj=Order.objects.get(id=order_product.order_id.id)
    order = order_product.order_id
    print(order)
    try:
        payment = order.payment
      
        if request.method == 'POST':
            reason = request.POST['cancelReason']
            if reason:
                order_product.return_reason = reason
            order.status = "Cancelled"

            payment.status = 'Order cancelled'
            order_product.item_cancel = True
            variant.stock += order_product.quantity

            if payment.payment_method != "Cashon Delivery":
                pass
             
            order.save()
            order_product.save()
            variant.save()
            payment.save()
        return redirect('order_summary',id=order_obj.id)
    except Exception as e:
        print(e)
    return redirect('order_summary',id=order_obj.id)
    
@cache_control(no_cache=True, no_store=True)
@login_required(login_url='user_login')
def order_return(request, order_id):
    order_item = OrderProduct.objects.get(id=order_id)
    try:
        if request.method == 'POST':
            return_reason = request.POST.get('returnReason', None)
            if return_reason:
                order_item.return_reason = return_reason
            order_item.return_request = True
        order_item.save()
        return redirect('order_summary',id=order_item.order_id.id)
    except Exception as e:
        print(e)

    return redirect('order_summary',id=order_id)

   