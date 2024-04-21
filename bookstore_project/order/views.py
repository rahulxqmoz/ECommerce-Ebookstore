from django.shortcuts import render,redirect
import pdb

from django.contrib.auth.decorators import login_required

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
    

   