from datetime import date
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render,redirect
import pdb
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from user_app.models import WalletBook
from buyproducts.models import Product_variant
from order.models import OrderProduct,Order
from django.core.mail import send_mail

# Create your views here.


def send_refund_email(email, amount):
    try:
        subject = 'Order Cancel'
        message = f'The .Amount Rs.{amount} is credited to your wallet as per you cancelled the order.Please Check your wallet!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(e)  


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
            send_refund_email(user.email,refund_amount)

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

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class ViewOrderInvoice(View):
    def get(self, request, order_id, *args, **kwargs):
        user = request.user
        try:
            id = OrderProduct.objects.get(id=order_id).order_id.id
            order = Order.objects.get(id=id)
            order_products = OrderProduct.objects.filter(order_id=order)
            data = {
                "company": "Ebook Store",
                "address": "Indira Nagar,Bengaluru",
                "city": "Bengaluru",
                "state": "Bengaluru",
                "zipcode": "570008",

                "phone": "+91 9745856542",
                "email": "ebook@gmail.com",
                "website": "ebookstore.com",
                "user": order.order_address.name,
                "customer_address": order.order_address.address,
                "town": order.order_address.town,
                "customer_email": user.email,
                "nearby_location": order.order_address.nearby_location,
                "district": order.order_address.district,
                "zip_code": order.order_address.zip_code,
                "state": order.order_address.state,
                "customer_phone": user.phone,
                "order_products": order_products,
                "order": order,
                'date':date.today()

            }

        except Exception as e:
            print(e)
            return HttpResponse(False)
        pdf = render_to_pdf('user/order_invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

class DownloadPDF(View):
    def get(self, request, order_id, *args, **kwargs):
        user = request.user
        try:
            id = OrderProduct.objects.get(id=order_id).order_id.id
            order = Order.objects.get(id=id)
            order_products = OrderProduct.objects.filter(order_id=order)
            data = {
                "company": "Ebook Store",
                "address": "Indira Nagar,Bengaluru",
                "city": "Bengaluru",
                "state": "Bengaluru",
                "zipcode": "570008",

                "phone": "+91 9745856542",
                "email": "ebook@gmail.com",
                "website": "ebookstore.com",
                "user": order.order_address.name,
                "customer_address": order.order_address.address,
                "town": order.order_address.town,
                "customer_email": user.email,
                "nearby_location": order.order_address.nearby_location,
                "district": order.order_address.district,
                "zip_code": order.order_address.zip_code,
                "state": order.order_address.state,
                "customer_phone": user.phone,
                "order_products": order_products,
                "order": order,
                'date':date.today()

            }
        except Exception as e:
            print(e)

        pdf = render_to_pdf('user/order_invoice.html', data)

        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" % ("12341231")
        content = "attachment; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response

def test_invoice(request,order_id):
    user = request.user
    try:
        id = OrderProduct.objects.get(id=order_id).order_id.id
        order = Order.objects.get(id=id)
        order_products = OrderProduct.objects.filter(order_id=order)
        data = {
            "company": "Ebook Store",
            "address": "Indira Nagar,Bengaluru",
            "city": "Bengaluru",
            "state": "Bengaluru",
            "zipcode": "570008",

            "phone": "+91 9745856542",
            "email": "ebook@gmail.com",
            "website": "ebookstore.com",
            "user": order.address.name,
            "customer_address": order.address.address,
            "town": order.address.town,
            "customer_email": user.email,
            "nearby_location": order.address.nearby_location,
            "district": order.address.district,
            "zip_code": order.address.zip_code,
            "state": order.address.state,
            "customer_phone": user.phone,
            "order_products": order_products,
            "order": order,
            'date':date.today()

        }

    except Exception as e:
        print(e)
        return HttpResponse(False)
    pdf = render_to_pdf('user/invoicetest.html', data)
    return HttpResponse(pdf, content_type='application/pdf')
