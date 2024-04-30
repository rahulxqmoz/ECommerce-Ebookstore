import calendar
from datetime import datetime, timedelta
import os
from calendar import month_name
import uuid
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from order.models import Order, OrderProduct
from cart.models import Coupon
from user_app.models import CustomUser
from buyproducts.models import *
from django.db.models import Sum,Count,Q,F
from django.utils import timezone
from django.db.models.functions import ExtractYear,ExtractMonth
from django.db.models.functions import Coalesce
# Create your views here.



# Sign in  section---------------------------------------------------------------------------

@cache_control(no_cache=True, no_store=True) 
def admin_login(request):
    if 'custom_user_id' in request.session:
        return redirect('admin_dashboard')

    if request.method=="POST":
        email=request.POST["email"]
        password=request.POST["password"]

        admin = authenticate(email=email,password=password)

        if admin:
            if admin.is_superuser:
                login(request,admin)
                request.session['custom_user_id'] = admin.id
                return redirect('admin_dashboard')
            else:
                messages.error(request,"You cant access this page with this credentials")    
        else:
            messages.error(request,"Inavlid Credentials")

            



    return render(request,'admin/admin_login.html')

@cache_control(no_cache=True, no_store=True) 
@staff_member_required(login_url="admin_login")
def admin_dashboard(request):
    context={}
    orders=[0]*12
    try:
        orders = Order.objects.all().order_by('-id')
        order_count = orders.count()
        order_total = Order.objects.aggregate(total=Sum('order_total'))['total']
        today = date.today()
        today_count = Order.objects.filter(created__date=today).count()
        today_revenue = Order.objects.filter(created__date=today).aggregate(total=Sum('order_total'))['total']
          
        # ----------------- Date filter ------------------------------

        if request.method == 'POST':
            try:
                date_from = request.POST.get('startDate')
                date_to = request.POST.get('endDate')

                date_format = '%Y-%m-%d'
                
                date_from = datetime.strptime(date_from, date_format)
                date_to = datetime.strptime(date_to, date_format)

                # Adjust end date to end of the day (23:59:59)
                date_to += timedelta(days=1)  # Move to the next day
                date_to -= timedelta(seconds=1)  # Go back one second to reach the end of the selected day

                # Filter orders within the specified range
                orders = Order.objects.filter(created__range=(date_from, date_to))
            except:
                pass
        # weekly sales data
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        weekly_count = Order.objects.filter(created__date__range=[week_start, week_end]).count()
        weekly_revenue = Order.objects.filter(created__date__range=[week_start, week_end]).aggregate(total=Sum('order_total'))['total']

        # Monthly sales data
        month_start = today.replace(day=1)
        month_end = month_start.replace(month=month_start.month % 12 + 1) - timedelta(days=1)
        monthly_count = Order.objects.filter(created__date__range=[month_start, month_end]).count()
        monthly_revenue = Order.objects.filter(created__date__range=[month_start, month_end]).aggregate(total=Sum('order_total'))['total']

        # Get the current year
        current_year = today.year

        # Get the start and end dates of the current year
        year_start = datetime(current_year, 1, 1)
        year_end = datetime(current_year, 12, 31)

        # Get the total sales count for the current year
        current_yearly_sales_count = Order.objects.filter(created__date__range=[year_start, year_end]).count()

        # Get the total sales revenue for the current year
        current_yearly_sales_revenue = Order.objects.filter(created__date__range=[year_start, year_end]).aggregate(total=Sum('order_total'))['total']

        # ------------------ Date filter end -----------------

        total_discount = Order.objects.aggregate(
        total_discount=Sum('discount_amount') + Sum('coupon_amount') + Sum('category_amount')
        )['total_discount']

        
        common_discount = total_discount if total_discount else 0
        month_names = [calendar.month_name[i] for i in range(1, 13)]

        yearly_sales = (
            Order.objects
            .annotate(year=ExtractYear('created'))
            .values('year')
            .annotate(year_total=Sum('order_total'))
            .order_by('year')
        )

        # calculate yearly orders

        yearly_orders = (
            Order.objects
            .annotate(year=ExtractYear('created'))
            .values('year')
            .annotate(total_orders=Count('id'))
            .order_by('year')
        )

       # Calculate monthly sales
        monthly_sales = (
            Order.objects
            .annotate(month=ExtractMonth('created'))  # Extract the month from the created field
            .values('month')  # Group by month
            .annotate(month_total=Sum('order_total'))  # Calculate total sales for each month
            .order_by('month')  # Order the results by month
        )

        # Calculate monthly orders
        monthly_orders = (
            Order.objects
            .annotate(month=ExtractMonth('created'))  # Extract the month from the created field
            .values('month')  # Group by month
            .annotate(total_orders=Count('id'))  # Count total orders for each month
            .order_by('month')  # Order the results by month
        )

        # Create lists to store the yearly data

        # ----------------- yearly sales section ended ----------------

        most_ordered_books = OrderProduct.objects.values('product__product__product_title').annotate(total_quantity=Coalesce(Sum('quantity'), 0)).order_by('-total_quantity')[:5]

        # Print or use the most ordered books
        book_names = [item['product__product__product_title'] for item in most_ordered_books]
        quantities = [item['total_quantity'] for item in most_ordered_books]
        current_year_start = datetime(datetime.now().year, 1, 1)
        yearly_order_totals = (
                Order.objects
                .filter(created__gte=current_year_start)
                .annotate(year=ExtractYear('created'))
                .values('year')
                .annotate(year_total=Sum('order_total'))
                .order_by('year')
        )
        start_year = 2020  # Change this to your start year
        current_year = datetime.now().year
        all_years = list(range(start_year, current_year + 1))

    # Retrieve the actual yearly sales data
        yearly_sales_data = {sale['year']: sale['year_total'] for sale in yearly_order_totals}

    # Populate the chart data
        chart_data = []
        for year in all_years:
            year_total = yearly_sales_data.get(year, 0)  # Get the total sales for the year, or set it to 0 if no data available
            chart_data.append(year_total)
            
        context={
                'order_count':order_count,'order_total':order_total,'today_count':today_count,
                'current_yearly_sales_count':current_yearly_sales_count,
                'today_revenue':today_revenue,'order':orders,
                'current_yearly_sales_revenue':current_yearly_sales_revenue,
                'yearly_sales':yearly_sales,
                'yearly_orders':yearly_orders,
                'weekly_count': weekly_count,
                'weekly_revenue': weekly_revenue,
                'monthly_count': monthly_count,
                'monthly_revenue': monthly_revenue,
                'total_discount':common_discount,
                'monthly_sales':monthly_sales,
                'monthly_orders':monthly_orders,
                'month_names': month_names,
                'book_names': book_names,
                'quantities': quantities,
                'yearly_order_totals':yearly_order_totals,
                'chart_data':chart_data,
                'all_years' :all_years
            }
    except Exception as e:
        print(e)    
    return render(request,'admin/admin_dashboard.html',context)

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# User management  section---------------------------------------------------------------------------

@cache_control(no_cache=True, no_store=True) 
@staff_member_required(login_url='admin_login')
def admin_user(request):
    context = {}
    try:
        users = CustomUser.objects.all()
        context = {
            'users': users,
        }
    except Exception as e:
        print(e)
    return render(request,'admin/admin_users.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_user_manage(request, id):
    try:
        user = CustomUser.objects.get(id=id)
       
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
    except Exception as e:
        print(e)

    return redirect('admin_users')

# Category Management section---------------------------------------------------------------------------

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_category(request):
    try:
        context={}
        offers=Offer.objects.all().order_by('-id')
        context={'offers':offers}
        if request.method=='POST':
            category_name=request.POST.get('categoryName')
            category_slug=category_name.replace(" ","-")
            category_discription=request.POST.get('categoryDescription')
            category_offer=request.POST.get('offer')
            cat_discount=request.POST.get('maxamount')
            max_discount=None
            cat_offer=None
            offer_obj=Offer.objects.get(id=category_offer)
            if category_offer is not '':
                if offer_obj.is_expired():
                        messages.error(request,'Offer expired')
                        return redirect('admin_category',context)
                else:
                    cat_offer=offer_obj
            else:
                cat_offer=None 
            if cat_discount is not '':
                max_discount=cat_discount
            else:
                max_discount=None                   
            
            exitscat=Category.objects.filter(category_name__iexact=category_name)
            if exitscat.exists():
                messages.error(request,"Category already exits")
                return redirect('admin_category',context)
            category=Category(category_name=category_name,category_description=category_discription,slug=category_slug,offer=offer_obj,max_discount=max_discount)
            
            if request.FILES:
                category.category_image=request.FILES['categoryImage']    


            category.save()
            messages.success(request,"Category Added")
            return redirect('admin_category',context)
        context={'offers':offers}        
    except Exception as e:
        print(e)        
    return render(request,'admin/admin_category.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_category_view(request):
    context = {}
    try:
        category = Category.objects.all().order_by('id')
        context = {
            'category': category,
        }
    except Exception as e:
        print(e)
    
    return render(request,'admin/admin_category_view.html',context)



@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_category(request,id):
    context ={}

    try:
        offers=Offer.objects.all().order_by('-id')
        category = Category.objects.get(id=id)
        context={'category':category,'offers':offers}
        if request.method=="POST":
            if request.FILES:
                os.remove(category.category_image.path)
                category.category_image=request.FILES['image']   
            
            category.category_name=request.POST.get('name') 
            category.category_description=request.POST.get('description')
            category_offer=request.POST.get('offer')
            cat_discount=request.POST.get('maxamount')
            if cat_discount != '':
                category.max_discount=cat_discount
            if category_offer != '':
                cat_offer=''
                offer_obj=Offer.objects.get(id=category_offer)
                if offer_obj.is_expired():
                        messages.error(request,'Offer expired')
                        return redirect('admin_edit_category',id=id)
                else:
                    cat_offer=offer_obj 
                category.offer=cat_offer

            else:
                print('null entered')
                category.offer=None    
            category.save()
            messages.success(request,"Edited Successfully")
            return redirect('admin_category_view')
        return render(request,'admin/admin_edit_category.html',context)



    except Exception as e:
        print(e)    
        return redirect('admin_category_view')
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_category(request,id):
    try:
        category=Category.objects.get(id=id)
       
        if category.is_active:

            category.is_active=False
            category.save()
            messages.success(request,"Unlist Successfully")
            
        else:
            category.is_active=True
            category.save()
            messages.success(request,"List Successfully") 
              

    except Exception as e:
        print(e)    
    return redirect('admin_category_view')


# Author management  section---------------------------------------------------------------------------

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_author(request):
    context = {}
    try:
        author = Author.objects.all().order_by('id')
        context = {
            'author': author,
        }
    except Exception as e:
        print(e)
    
    return render(request,'admin/admin_author.html',context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_author(request):
    try:
        if request.method=='POST':
            author_name=request.POST.get('authorname')
            token = str(uuid.uuid4())
            author_slug=token
            author_description=request.POST.get('authordesc')
            existauthor=Category.objects.filter(category_name__iexact=author_name)
            if existauthor.exists():
                messages.error(request,"Author already exits")
                return redirect('admin_add_author')
            author=Author(author_name=author_name,author_description=author_description,slug=author_slug)
            
            if request.FILES:
                author.author_image=request.FILES['authorimage']    


            author.save()
            messages.success(request,"Author Added")
            return redirect('admin_add_author')
            
    except Exception as e:
        print(e)
        messages.error(request,"Author save failed")
        return redirect('admin_add_author')        

    return render(request,'admin/admin_add_author.html')

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_author(request,id):
    context ={}

    try:
        author = Author.objects.get(id=id)
        context={'author':author}
        if request.method=="POST":
            if request.FILES:
                os.remove(author.author_image.path)
                author.author_image=request.FILES['image']   
         
            author.author_name=request.POST.get('name') 
            author.author_description=request.POST.get('description')

            author.save()
            messages.success(request,"Edited Successfully")
            return redirect('admin_author')
        return render(request,'admin/admin_edit_author.html',context)



    except Exception as e:
        print(e)    
        return redirect('admin_author')
    
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_author(request,id):
    try:
        author=Author.objects.get(id=id)
       
        if author.is_active:

            author.is_active=False
            author.save()
            messages.success(request,"Unlist Successfully")
        else:
            author.is_active=True
            author.save() 
            messages.success(request,"List Successfully") 
               

    except Exception as e:
        print(e)    
    return redirect('admin_author')


# Offer section---------------------------------------------------------------------------


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_offer(request):
    try:

        if request.method=='POST':
            offer_name=request.POST.get('offername')
            off_percent = request.POST.get('offpercent')
            
            existoffer=Offer.objects.filter(name__iexact=offer_name)
            if existoffer.exists():
                messages.error(request,"Offer already exits")
                return redirect('admin_add_offer')
            
            validFrom=request.POST.get('valid_from')
            validTo=request.POST.get('valid_to')
            offer=Offer(name=offer_name,off_percent=off_percent,start_date=validFrom,end_date=validTo)
            offer.save()
            messages.success(request,"offer Added")
            return redirect('admin_add_offer')
            
    except Exception as e:
        
        print(e)
        messages.error(request,"offer save failed")
        return redirect('admin_add_offer')
    return render(request,'admin/admin_add_offer.html')

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_offer(request):
    context = {}
    try:
        offer = Offer.objects.all().order_by('id')
        context = {
            'offer': offer,
        }
    except Exception as e:
        print(e)
    return render(request,'admin/admin_offer.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_offer(request,id):
    context ={}

    try:
        offer = Offer.objects.get(id=id)
        context={'offer':offer}
        if request.method=="POST":
               

            offer.name=request.POST.get('offername') 
            offer.off_percent=request.POST.get('offpercent')

            offer.start_date=request.POST.get('valid_from')
            offer.end_date=request.POST.get('valid_to')

            offer.save()
            messages.success(request,"Edited Successfully")
            return redirect('admin_offer')
        return render(request,'admin/admin_edit_offer.html',context)



    except Exception as e:
        print(e)    
        return redirect('admin_offer')



    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_offer(request,id):
    try:
        offer=Offer.objects.get(id=id)
       
        if offer.is_active:

            offer.is_active=False
            offer.save()
            messages.success(request,"Unlist Successfully")
        else:
            offer.is_active=True
            offer.save() 
            messages.success(request,"List Successfully") 
               

    except Exception as e:
        print(e)    
    return redirect('admin_offer')

# Products section---------------------------------------------------------------------------

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_product(request):
    try:
        if request.method=="POST":
            product_name=request.POST.get('productname')
            product=Products.objects.filter(product_title__iexact=product_name)
            token=product_name.replace(" ","-")
            if product.exists():
                messages.error(request,"Prodcut already exists!!")
                return redirect('admin_add_product')
            
            productsave=Products(product_title=product_name,slug=token)
            
              
            if request.FILES:
                productsave.product_image=request.FILES['productimage']

            product_description=request.POST.get('productdesc') 
            productsave.product_description=product_description
            productsave.save()

            messages.success(request,"Product Added Successfully!!")

    except Exception as e:
        print(e)
        messages.error(request,"Product Added Failed?!")
        return redirect('admin_add_product')    
    return render(request,'admin/admin_add_products.html')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_product(request):
    context = {}
    try:
        products = Products.objects.all().order_by('id')
        context = {
            'products': products,
        }
    except Exception as e:
        print(e)
    return render(request,'admin/admin_products.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_product_edit(request,id):
    context ={}

    try:
        product = Products.objects.get(id=id)
        context={'product':product}
        if request.method=="POST":
            if request.FILES:
                os.remove(product.product_image.path)
                product.product_image=request.FILES['image']   

            product.product_title=request.POST.get('name') 
            product.product_description=request.POST.get('description')

            product.save()
            messages.success(request,"Edited Successfully")
            return redirect('admin_product')
        return render(request,'admin/admin_edit_product.html',context)



    except Exception as e:
        print(e)
        messages.error(request,"Cannot Find The File?!")    
        return redirect('admin_product')
    


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_product_delete(request,id):
    try:
        product=Products.objects.get(id=id)
       
        if product.is_active:

            product.is_active=False
            product.save()
            messages.success(request,"Unlist Successfully")
        else:
            product.is_active=True
            product.save() 
            messages.success(request,"List Successfully") 
               

    except Exception as e:
        print(e)    
    return redirect('admin_product')


# Editions section ----------------------------------------------------------------------------------


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edition(request):
    context = {}
    try:
        editions = Editions.objects.all().order_by('id')
        context = {
            'editions': editions,
        }
    except Exception as e:
        print(e)
    
    return render(request,'admin/admin_edition.html',context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_edition(request):
    try:
        if request.method=='POST':
            edition_name=request.POST.get('editioname')
            token = edition_name.replace(" ","-")
            edition_slug=token
            edition_description=request.POST.get('editiondesc')
            year=request.POST.get('year')
            publisher=request.POST.get('publisher')
            existedition=Editions.objects.filter(editons_name__iexact=edition_name)
            if existedition.exists():
                messages.error(request,"Edition already exits")
                return redirect('admin_add_edition')
            edition=Editions(editons_name=edition_name,edition_description=edition_description,slug=edition_slug,publication_year=year,publisher=publisher)
            
            


            edition.save()
            messages.success(request,"Edition Added")
            return redirect('admin_add_edition')
            
    except Exception as e:
        print(e)
        messages.error(request,"Edition save failed")
        return redirect('admin_add_edition')        

    return render(request,'admin/admin_add_edition.html')

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_edition(request,id):
    context ={}

    try:
        edition = Editions.objects.get(id=id)
        context={'edition':edition}
        if request.method=="POST":
              

            edition.editons_name=request.POST.get('name') 
            edition.edition_description=request.POST.get('description')
            edition.publication_year=request.POST.get('year') 
            edition.publisher=request.POST.get('publisher')

            edition.save()
            messages.success(request,"Edited Successfully")
            return redirect('admin_edition')
        return render(request,'admin/admin_edit_edition.html',context)



    except Exception as e:
        print(e)    
        return redirect('admin_edition')
    
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_edition(request,id):
    try:
        edition=Editions.objects.get(id=id)
       
        if edition.is_active:

            edition.is_active=False
            edition.save()
            messages.success(request,"Unlist Successfully")
        else:
            edition.is_active=True
            edition.save() 
            messages.success(request,"List Successfully") 
               

    except Exception as e:
        print(e)    
    return redirect('admin_edition')




# Products variant section---------------------------------------------------------------------------

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def add_product_variant(request):

    context={}

    try:
        products=Products.objects.all().order_by('id')
        author=Author.objects.all().order_by('id')
        offers=Offer.objects.all().order_by('id')
        categories=Category.objects.all().order_by('id')
        editions=Editions.objects.all().order_by('id')

        if request.method=="POST":
            product=request.POST.get('product')
            category=request.POST.get('category')
            auth=request.POST.get('author')
            offer=request.POST.get('offer')
            price=request.POST.get('price')
            stock=request.POST.get('stock')
            rating=request.POST.get('rating')
            edition=request.POST.get('edition')

            productobj=Products.objects.get(id=product)
            categoryobj=Category.objects.get(id=category)
            authprobj=Author.objects.get(id=auth)
            offerobj=Offer.objects.get(id=offer)
            editionobj=Editions.objects.get(id=edition)

            
            variant_name=f"{productobj.product_title} {authprobj.author_name} {editionobj.editons_name}"
            variant_name_without_periods = variant_name.replace(".", "")
            variant_slug=variant_name_without_periods.replace(" ","-")

            try:


                variant = Product_variant.objects.get(product=productobj,author=authprobj,edition=editionobj)
                
                messages.error(request,"Variant already exists")
            except Product_variant.DoesNotExist:

                variant = Product_variant(
                    slug=variant_slug,
                    variant_name=variant_name,
                    product=productobj,
                    author=authprobj,
                    category=categoryobj,
                    product_price=price,
                    stock=stock,
                    rating=rating,
                    offer=offerobj,
                    edition=editionobj
                )
                # variant_pro=Product_variant(slug=variant_slug,variant_name=variant_name,product=product,
                #         author=auth,category=category,product_price=price,stock=stock,rating=rating,offer=offer)
                
                variant.save()
                    # multiple image fetching
                try:
                    multiple_images = request.FILES.getlist('multipleImage', None)
                    if multiple_images:
                        for image in multiple_images:
                            photo = MultipleImages.objects.create(
                                product=variant,
                                images=image,
                            )

                except Exception as e:
                    print(e)
                    messages.success(request,"Image Upload Failed") 
                    return redirect('admin_add_product_variant')  
                    

                messages.success(request,"Product Variant Successfully added!")  
                return redirect('admin_add_product_variant')  


        context={
            'products':products,
            'authors':author,
            'offers':offers,
            'categories':categories,
            'editions':editions
        }

    except Exception as e:
        print(e)
        return redirect('admin_add_product_variant')    

    return render(request,'admin/admin_product_variant.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_productvariant(request):
    context = {}
    try:
        vairant = Product_variant.objects.all().order_by('-id')
        variant_images = {}

        for variant in vairant:
            images = MultipleImages.objects.filter(product=variant)
            variant_images[variant.id] = list(images)
            
            
        print(variant_images)    
        context = {
            'vairant': vairant,
            'variant_images':variant_images
        }
    except Exception as e:
        print(e)
    
    return render(request,'admin/admin_view_productvariant.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_variant(request,id):
    try:
        variant=Product_variant.objects.get(id=id)
       
        if variant.is_active:

            variant.is_active=False
            variant.save()
            messages.success(request,"Unlist Successfully")
        else:
            variant.is_active=True
            variant.save() 
            messages.success(request,"List Successfully") 
               

    except Exception as e:
        print(e)    
    return redirect('admin_productvariant')
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_variant(request,id):
    context={}

    try:
        variant=Product_variant.objects.get(id=id)
        products=Products.objects.all().order_by('id')
        author=Author.objects.all().order_by('id')
        offers=Offer.objects.all().order_by('id')
        categories=Category.objects.all().order_by('id')
        editions=Editions.objects.all().order_by('id')
        object_image = MultipleImages.objects.filter(product=id)

        if request.method=="POST":
            product=request.POST.get('product')
            category=request.POST.get('category')
            auth=request.POST.get('author')
            offer=request.POST.get('offer')
            price=request.POST.get('price')
            stock=request.POST.get('stock')
            rating=request.POST.get('rating')
            edition=request.POST.get('edition')

            productobj=Products.objects.get(id=product)
            categoryobj=Category.objects.get(id=category)
            authprobj=Author.objects.get(id=auth)
            offerobj=Offer.objects.get(id=offer)
            editionobj=Editions.objects.get(id=edition)

            variant.product=productobj
            variant.category=categoryobj
            variant.author=authprobj
            variant.offer=offerobj
            variant.edition=editionobj
            variant.product_price=price
            variant.stock=stock
            variant.rating=rating
           
            
            multiple_images = request.FILES.getlist('multipleImage', None)
            if multiple_images:
                if object_image:
                    for image in object_image:
                        os.remove(image.images.path)
                        image.delete()
                    for image in multiple_images:
                        img=MultipleImages.objects.create(
                            product=variant,
                            images=image
                        )  
                else:
                    for image in multiple_images:
                        img=MultipleImages.objects.create(
                            product=variant,
                            images=image
                        )   
            variant_name=f"{productobj.product_title} {authprobj.author_name} {editionobj.editons_name}"
            variant.variant_name=variant_name           
            variant.save()         
            messages.success(request,"Edited Successfully") 
            return redirect('admin_productvariant')                

                  


        context={
            'variant':variant,
            'products':products,
            'authors':author,
            'offers':offers,
            'categories':categories,
            'editions':editions,
            'multiple_images':object_image
        }


    except Exception as e:
        print(e)    




    return render(request,'admin/admin_edit_productvariant.html',context)

def delete_image(request, image_id):
    try:

        image = MultipleImages.objects.get(id=image_id)
        variant_id = image.product.id
        image.delete()
        messages.success(request,'Delete successfull')
        return redirect('admin_edit_variant',id=variant_id)
    except Exception as e:
        messages.success(request,'Delete Failed')
        return redirect('admin_edit_variant',id=variant_id)    

#Coupon----------------------------------------------------------------------------------------



@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_coupon(request):
    try:

        if request.method=='POST':
            couponcode=request.POST.get('couponcode')
            off_percent = request.POST.get('offpercent')
            min_amount = request.POST.get('minamount')
            max_discount = request.POST.get('maxdiscount')
            couponstock=request.POST.get('couponstock')
            expiry_date_str = request.POST.get("expirydate")

            
            
            # Validate coupon_code
            if couponcode and couponcode.islower():
                messages.warning(request, "Coupon code cannot contain small letters!")
                return redirect('admin_add_coupon')
            
            if Coupon.objects.filter(coupon_code=couponcode).exists():
                messages.warning(request, "this coupon is already in your account!")
                return redirect('admin_add_coupon')

            # Validate min_amount
            if not min_amount.isdigit() or int(min_amount) < 500:
                messages.warning(request, "Minimum amount must be a number greater than or equal to 500!")
                return redirect('admin_add_coupon')

            # Validate off_percent
            if not off_percent.isdigit() or int(off_percent) <= 0:
                messages.warning(request, "Off percent must be a positive number greater than 0!")
                return redirect('admin_add_coupon')

            # Validate max_discount
            if not max_discount.isdigit() or int(max_discount) < int(off_percent):
                messages.warning(request, "Max discount must be a number greater than or equal to Off percent!")
                return redirect('admin_add_coupon')
            
            # Validate expiry_date
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                messages.warning(request, "Invalid expiry date format. Please use YYYY-MM-DD.")
                return redirect('admin_add_coupon')

            if expiry_date <= timezone.now().date():
                messages.warning(request, "Expiry date should be in the future!")
                return redirect('admin_add_coupon')

            coupon = Coupon.objects.create(
                        coupon_code = couponcode,
                        min_amount = min_amount,
                        off_percent = off_percent,
                        max_discount = max_discount,
                        expiry_date = expiry_date_str,
                        coupon_stock=couponstock
                    ).save()
            
            
            messages.success(request,"Coupon Added")
            return redirect('admin_add_coupon')
            
    except Exception as e:
        
        print(e)
        messages.error(request,"Coupon save failed")
        return redirect('admin_add_coupon')
    return render(request,'admin/admin_add_coupon.html')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_coupon(request):
    context = {}
    try:
        coupons = Coupon.objects.all().order_by('-id')
        context = {
            'coupons': coupons,
        }
    except Exception as e:
        print(e)
    return render(request,'admin/admin_coupon.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_coupon(request,id):
    try:
        coupon=Coupon.objects.get(id=id)
       
        if coupon.is_active:

            coupon.is_active=False
            coupon.save()
            messages.success(request,"Unlist Successfully")
        else:
            coupon.is_active=True
            coupon.save() 
            messages.success(request,"List Successfully") 
               

    except Exception as e:
        print(e)    
    return redirect('admin_coupon')

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_coupon(request, id):
    try:
        if request.method == "POST":
            coupon_code = request.POST.get("couponcode")
            min_amount = request.POST.get("minamount")
            off_percent = request.POST.get("offpercent")
            max_discount = request.POST.get("maxdiscount")
            expiry_date_str = request.POST.get("expirydate")
            coupon_stock = request.POST.get("couponstock")

            if Coupon.objects.exclude(id=id).filter(coupon_code=coupon_code).exists():
                messages.error(request, 'Coupon code must be unique.')
                return redirect('admin_edit_coupon',id=id)

            Coupon.objects.filter(id = id).update(
                coupon_code = coupon_code,
                min_amount = min_amount,
                off_percent = off_percent,
                max_discount = max_discount,
                expiry_date = expiry_date_str,
                coupon_stock=coupon_stock
            )
            messages.success(request, f'{coupon_code} updated succesfully.')
            return redirect('admin_coupon')

        coupon = Coupon.objects.get(id=id)
        context = {
            'coupon': coupon
        }
        return render(request, 'admin/admin_edit_coupon.html', context)
    except Exception as e:
        print(e)
        messages.error(request, 'Edit Failed!!')
        return render(request, 'admin/admin_edit_coupon.html', context)    

#------------Order Managment-------------------------------------------------------
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_order(request):
    context = {}
    try:
        orders = Order.objects.all().order_by('-id')
        context = {
            'orders': orders,
        }
    except Exception as e:
        print(e)
    return render(request,'admin/admin_order.html',context)

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_order_update(request,id):
    context = {}
    try:
        order = Order.objects.get(id=id)
        order_items = OrderProduct.objects.filter(order_id=id)
        payment = order.payment
        if request.method == 'POST':
            order_status = request.POST.get('orderStatus', None)
            if order_status:
                order.status = order_status
                order.save()
            if order_status == 'Delivered':
                payment.is_paid = True
            payment.save()
            messages.success(request, 'Status updated')
            return redirect('admin_order_update', id)
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'admin/admin_order_update.html', context)
    except Exception as e:
        print(e)
    
    return render(request,'admin/admin_order_update.html')

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def return_request(request, id):
    try:

        order_item = OrderProduct.objects.get(id=id)
        variant = order_item.product
        order = order_item.order_id
        order_id = order.id
       
        user = order.user
        shipping_cost=0
        deduct_discount=0
        tax=0
        coupon=0
        count =OrderProduct.objects.filter(order_id=order).count()
        
        if order.shipping_cost>0:
            if count < order.shipping_cost:
                shipping_cost=order.shipping_cost/count

       
        if order.coupon_amount:    
            if count<order.coupon_amount:      
                coupon = order.coupon_amount/count


        if order.tax:
            if count<order.tax:      
                tax = order.tax/count
        if request.method == 'POST':
            order_item.is_returned = True
            variant.stock += order_item.quantity
            amount = int(variant.offerprice()) * order_item.quantity
            if coupon>0:
                amount=amount-coupon
            if tax>0:
                amount=amount+tax

            refund_amount = (float(amount) + float(shipping_cost)) # calculating refund amount.
           
            user.wallet = float(user.wallet) + float(refund_amount)
            wallet_acc = WalletBook()
            wallet_acc.customer = user
            wallet_acc.amount = refund_amount
            wallet_acc.description = "Refund Credited for Product Return"
            wallet_acc.increment = True
            wallet_acc.save()
            order_item.save()
            variant.save()
            user.save()
            order.save()
            return redirect('admin_order_update', order_id)
    except Exception as e:
        print(e)
        return redirect('admin_order')
#----------------------------------------------Reports------------------------------------


@staff_member_required(login_url='admin_login')
def reports(request):
    context = {}
    try:
        products = Product_variant.objects.all()
        cancel_orders = OrderProduct.objects.filter(item_cancel=True)

        context = {
            'products': products,
            'cancel_orders': cancel_orders,
        }
    except Exception as e:
        print(e)

    return render(request, 'admin/admin_reports.html', context)