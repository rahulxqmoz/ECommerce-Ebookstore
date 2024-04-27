from decimal import Decimal
from django.shortcuts import render,redirect
import pdb

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from user_app.models import WalletBook
from buyproducts.models import Product_variant
from order.models import OrderProduct,Order
# Create your views here.
@login_required(login_url='user_login')
def cancel_order(request,id):

    
    try:
        if 'user' in request.session:
            user = request.user
        order_product = OrderProduct.objects.get(id=id)
        variant = Product_variant.objects.get(id=order_product.product.id)
        order_obj=Order.objects.get(id=order_product.order_id.id)
        order = order_product.order_id
        payment = order.payment
      
        if request.method == 'POST':
            reason = request.POST['cancelReason']
            if reason:
                order_product.return_reason = reason
            order.status = "Cancelled"
            payment.status = 'Order cancelled'
            #getting ordered products from this order id
            ordered_proc_obj=OrderProduct.objects.filter(order_id=order_obj)
            for item in ordered_proc_obj:
                variant_obj = Product_variant.objects.get(id=item.product.id)
                item.item_cancel = True
                item.return_reason=reason
                variant_obj.stock += item.quantity
                variant_obj.save()  # Save changes inside the loop
                item.save()

            if payment.payment_method != "Cashon Delivery":
                amount = order.order_total
                refund_amount = float(amount)  # Refund amount total
                user.wallet += Decimal(refund_amount)  # Update wallet amount directly
                user.save()

                wallet = WalletBook.objects.create(
                    customer=user,
                    description="Cashback received due to the cancel of item",
                    increment=True,
                    amount=str(refund_amount)
                )

            order.save()  # Save order changes
            payment.save()  # Save payment changes

        return redirect('order_summary', id=order_obj.id)

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

   