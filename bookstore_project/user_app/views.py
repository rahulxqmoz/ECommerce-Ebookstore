from decimal import Decimal
import random
import uuid
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q,Count
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.urls import reverse
from django.utils.html import format_html
from validate_email import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.conf import settings
from django.shortcuts import redirect, render
import razorpay
from order.models import *
from cart.models import CartItem
from user_app.models import CustomUser,Forgotpassword
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from buyproducts.models import *
# Create your views here.


def generate_referral_code():
    code = str(uuid.uuid4()).replace('-', '')[:12]
    return code


def index(request):
    try:
        if 'custom_user_id' in request.session:
            return redirect('admin_dashboard')
        
        context={}

        products=Product_variant.objects.filter(product__is_active=True,  is_active=True)
        
        list_product=[]
        category=Category.objects.all().order_by('id')
        offers = {}

        for offer in products:
            if offer.offerprice() > 0 and offer.catoffer() > 0:
                offerprice = min(offer.offerprice(), offer.catoffer())
                offers[offer.id] = offerprice
                
            elif offer.offerprice() > 0:
                offerprice = offer.offerprice()
                offers[offer.id] = offerprice

            elif offer.catoffer() > 0:
                offerprice = offer.catoffer()
                offers[offer.id] = offerprice 

            else:
                offerprice = offer.product_price
                offers[offer.id] = offerprice

        if 'user' in request.session:        
            user_id=CustomUser.objects.get(id=request.user.id)
            if user_id:
                cartitem=CartItem.objects.filter(customer=user_id).count()
                request.session['cart_item_count'] = cartitem
                wishcount = wishlist=Wishlist.objects.filter(user=user_id).count()
                request.session['wishlishcount']=wishcount
        else:
            request.session['cart_item_count'] = 0
            request.session['wishlishcount']=0
        
        for i in range(len(products)):
            list_product.append(products[i])

        context={
            'listproducts':list_product,
            'offerprice':offers,
            'category':category,
            'count':request.session.get('cart_item_count', 0)
        }


        return render(request,'user/index.html',context)
    except Exception as e:
        print(e)
        logout(request)
        return render(request,'user/index.html',context)

def user_sign_up(request):
    try:
        if 'custom_user_id' in request.session:
            return redirect('admin_dashboard')
        if 'user' in request.session:
            return redirect('index')
        if request.method=="POST":
            
            field_names = ['first_name', 'last_name', 'email', 'phonenumber', 'password', 'c_passsword',
                            'referral_code']
            user_data = {field: request.POST.get(field, '') for field in field_names}

            exist_email = CustomUser.objects.filter(email=user_data['email'])
            exist_phone = CustomUser.objects.filter(phone=user_data['phonenumber'])
            
            is_valid = validate_email(user_data['email'])

            if is_valid == False:
                messages.error(request,'Enter a valid email address!!')
                return redirect('user_sign_up')


            if exist_email:
                messages.error(request,"Email already exists")
            elif exist_phone:
                messages.error(request,"phone number already exists")
            elif len(user_data['phonenumber'])!=10:
                messages.error(request,"Enter valid phone number!")    
            else:
                if (user_data['password']==user_data['c_passsword']):
                    hashed_password = make_password(user_data['password'])

                    user = CustomUser.objects.create(first_name=user_data['first_name'],password=hashed_password, phone=user_data['phonenumber'],last_name=user_data['last_name'],email=user_data['email'])    
                    otp = get_random_string(length=6, allowed_chars='1234567890')
                    code = generate_referral_code()

                    user.otp=otp
                    user.referral_code=code

                    # #validate_email(user_data['email'])
                    # try:
                    #     validate_email(user_data['email'])
                    #     send_otp_email(user_data['email'],otp)
                    # except ValidationError:
                    #     messages.error(request, "Enter a valid email address")
                    #     return redirect('user_sign_up')

                   
                    # if not validate_email(user_data['email']):
                    #     messages.error(request, "Enter a valid email address")
                    #     return redirect('user_sign_up')
                    # else:
                    #     send_otp_email(user_data['email'],otp)
                    send_otp_email(user_data['email'],otp)
                    try:
                        if user_data['referral_code']:
                            ref_user = CustomUser.objects.filter(referral_code=user_data['referral_code']).first()
                            if ref_user:
                                referred_user = CustomUser.objects.get(id=ref_user.id)
                                referred_user.wallet += 200
                                user.wallet = 50
                                user.referred_by = referred_user.email
                                referred_user.save()
                                wallet_acc = WalletBook()
                                wallet_acc.customer = referred_user
                                wallet_acc.amount =  referred_user.wallet
                                wallet_acc.description = "Referal Bonus Credited"
                                wallet_acc.increment = True
                                wallet_acc.save()
                                messages.success(request, "Referral code verified")
                            else:
                                messages.error(request, "Invalid Referral code.")
                    except Exception as e:
                        print(e)
                    user.save()
                    if user.wallet>0:
                        wallet_acc = WalletBook()
                        wallet_acc.customer = user
                        wallet_acc.amount =  user.wallet
                        wallet_acc.description = "Sign up bonus credited"
                        wallet_acc.increment = True
                        wallet_acc.save()
                
                
                    return redirect('otp_verification',user_id=user.id)
                else:
                    messages.error(request,"Password did'nt match!!")
    except Exception as e:
        print(e)     
        messages.error(request,"Unexpected error occured!!")     

    return render(request,'user/signup.html')



@cache_control(no_store=True, no_cache=True)
def otp_verification(request,user_id):
    if 'custom_user_id' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        return redirect('index')
    user =CustomUser.objects.get(id=user_id)

    context={'user':user}

    try:
        if request.method=='POST':
            otp=request.POST['otp']

            if(len(otp)==6):
                if otp == user.otp:
                    user.is_verified=True
                    user.otp = ''
                    user.save()
                    if user.wallet > 0 :
                        messages.success(request, f"Account verified.You got a referal amount of Rs.{user.wallet} in your wallet.")
                        return redirect('user_login')
                    else:
                        messages.success(request, "Account verified.")
                        return redirect('user_login')
                else:
                    messages.error(request, 'Invalid OTP.')
                    return redirect('otp_verification', user.id)
            else:
                messages.error(request, "Invalid OTP")
                return redirect('otp_verification', user.id)
        if not user.otp:
            
            user.delete()
            messages.error(request, "OTP expired and registration cancelled.")
            return redirect('user_sign_up')  

    except Exception as e:
        print(e)        

    return render(request,"user/otp_verification.html",context)

cache_control(no_store=True, no_cache=True)
def regenerate_otp(request,user_id):
        if 'custom_user_id' in request.session:
            return redirect('admin_dashboard')
        if 'user' in request.session:
            return redirect('index')
        try:
            user = CustomUser.objects.get(id=user_id)
            email = user.email
            user.otp = ''
            otp = get_random_string(length=6, allowed_chars='1234567890')

            send_otp_email(email,otp)

            user.otp = otp
            user.save()
            messages.success(request, "OTP sent to your mail")
        except Exception as e:
            print(e)
        return redirect('otp_verification', user_id)
    
def cancel_registration(request,user_id):
    try:
       
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        messages.error(request,"Registration of user is cancelled")
        return redirect('user_sign_up')
    except Exception as e:
        print(e)
        messages.error(request,"Cancellation failed")
        return redirect('user_sign_up')

    
@cache_control(no_store=True, no_cache=True)
def user_login(request):
    
    if 'custom_user_id' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        return redirect('index')
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request,email=email, password=password)
            if user is not None and  user.is_superuser==False and user.is_verified==True:
                    login(request, user)
                    request.session['user'] = email
                    return redirect('index')
            else:
                    messages.error(request, 'Invalid email or password')
    except Exception as e:
        print(e)  
        messages.error(request, 'Invalid email or password')              
        return redirect('user_login')
    return render(request, 'user/login.html')

       




def send_otp_email(email, otp):
    try:
        subject = 'Your One-Time Password (OTP)'
        message = f'Your OTP is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(e)    




def user_forgotpassword(request):
    if 'custom_user_id' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        return redirect('index')
    try:
        if request.method == 'POST':
            email = request.POST.get('email', None)
            if email:
                my_user = CustomUser.objects.filter(email=email).first()
                if my_user.is_active==True:
                    token = str(uuid.uuid4())
                    
                    forgot_password_instance, created = Forgotpassword.objects.get_or_create(user=my_user)
                    forgot_password_instance.forgot_password_token = token
                    forgot_password_instance.save()

                    

                    send_forget_password_mail(email, token)
                    messages.success(request, "Password reset link sent to the email.")
                    return redirect('user_login')
                else:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Email is required.")
    except Exception as e:
        print(e)
        messages.error(request, "Forgot password send failed.")
        return redirect('forgot_password')
    return render(request, 'user/forgotpassword.html')

def change_password(request,token):
    if 'custom_user_id' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        return redirect('index')
    context={}

    try:
        profile_obj=Forgotpassword.objects.filter(forgot_password_token=token).first()

        if request.method=="POST":
            newpassword=request.POST.get('new_password')
            c_password=request.POST.get('reconfirm_password')
            user = request.POST.get('user_id')

            if user is None:
                messages.error(request,"No user Found")
                return redirect(f"/reset-password/{token}/")
            
            if newpassword == c_password:
                user_obj=CustomUser.objects.get(id=user)

                

                user_obj.set_password(newpassword)
                user_obj.save()
                messages.success(request,"Password successfully changed.")
                return redirect('user_login')

            else:
                messages.error(request,"Password doesnt match")
                return redirect(f"/reset-password/{token}/")



        context={'user_id':profile_obj.user.id}
    except Exception as e:
        print(e)    
    return render(request,'user/reset-password.html',context)

@cache_control(no_store=True, no_cache=True)
def user_logout(request):
    logout(request)
    return redirect('index')


def send_forget_password_mail(email, token):
    try:
        subject = "Forgot password"
        message = f'Hi, click the link to reset your password http://127.0.0.1:8000/reset-password/{token}/'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(e)

def product_detail(request,id):
    try:
        product=Product_variant.objects.get(id=id)
        product_images=MultipleImages.objects.filter(product=product)
        offerprice=0
        # off_percent=product.offer.off_percent
        # if off_percent:
        #     offerprice=int(product.product_price)- int(product.product_price) * (int(off_percent)/100)
        rating_stars=range(product.rating) if product.rating > 0 else range(0)    
        category=Category.objects.all().order_by('id')
        review=ProductReview.objects.filter(product=product)

        print(product.catoffer())
        print(product.offerprice())
        
        
        context={}

        related_products = Product_variant.objects.filter(
        Q(category=product.category) | Q(author=product.author) | Q(edition=product.edition)
        )
        relatedoffer={}
        # for offer in related_products:
        #     offerprice=int(offer.product_price)- int(offer.product_price) * (int(offer.offer.off_percent)/100)
        #     relatedoffer[offer.id] =offerprice

    
        context={
            'productinfo':product,
            'product_images':product_images,
            'category':category,
            'review':review,
            'listproducts':related_products,
            
            
        }    

        return render(request,'user/product_detail.html',context)
    except Exception as e:
        print(e)
        messages.error(request,"Page not found")
        return redirect('index')

def browse_products(request):
    try:
        context={}

        products=Product_variant.objects.filter(Q(is_active=True) & Q(product__is_active=True))
        category=Category.objects.all().order_by('id')
        offers = {}

        for offer in products:
            if offer.offerprice() > 0 and offer.catoffer() > 0:
                offerprice = min(offer.offerprice(), offer.catoffer())
                offers[offer.id] = offerprice
                
            elif offer.offerprice() > 0:
                offerprice = offer.offerprice()
                offers[offer.id] = offerprice

            elif offer.catoffer() > 0:
                offerprice = offer.catoffer()
                offers[offer.id] = offerprice 

            else:
                offerprice = offer.product_price
                offers[offer.id] = offerprice
            

            
           
                   
                
         
        sort_criteria = request.GET.get('sort_criteria')
        if sort_criteria:
            if(sort_criteria=="newest"):
                products=Product_variant.objects.filter(is_active=True).order_by('-created_date')
            if sort_criteria == "price_low_to_high":
                products = Product_variant.objects.filter(is_active=True)
                products = sorted(products, key=lambda x: x.price_sub_total())
            if sort_criteria == "price_high_to_low":
                products = Product_variant.objects.filter(is_active=True)
                products = sorted(products, key=lambda x: x.price_sub_total(), reverse=True)
            if(sort_criteria=="popular"):
                products_popular = OrderProduct.objects.values('product').annotate(buy_count=Count('id')).order_by('-buy_count')
                
                products =  Product_variant.objects.annotate(
                buy_count=Count('orderproduct')
                ).order_by('-buy_count') 
            print(sort_criteria)    

            try:     
                category_obj= Category.objects.get(id=sort_criteria)
                if category_obj:
                    products=Product_variant.objects.filter(Q(is_active=True) & Q(category=category_obj)).order_by('-id')
            except:
                if(sort_criteria=='0'):
                    products=Product_variant.objects.filter(Q(is_active=True) & Q(product__is_active=True)) 

         # Paginate the products
        paginator = Paginator(products, 6)  # Show 6 products per page
        page_number = request.GET.get('page')
        try:
            paginated_products = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paginated_products = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginated_products = paginator.page(paginator.num_pages)    


        context={
            'listproducts':paginated_products,
            'offerprice':offers,
            'category':category
        }
        return render(request,'user/browse_products.html',context)
    except Exception as e:
        print(e)
        messages.error(request,"Page not found")
        return redirect('index')


def write_review(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        try:    
            if request.method=="POST":
                print("Hello")
                rating=request.POST.get('rating')
                review_desc=request.POST.get('review_desc')
                product_id=request.POST.get('id')
                title=request.POST.get('title')
                if product_id is None:  
                    return HttpResponse("Product ID is missing in the form data.")
                product=Product_variant.objects.get(id=product_id)
                print(product.variant_name)
                user_id = CustomUser.objects.get(id=request.user.id)

                try:
                    reviewcheck= ProductReview.objects.get(user=user_id,product=product)
                    if reviewcheck:
                        messages.error(request,'Review already exists!!!')
                        return redirect('product_detail',id=product_id)
                except ProductReview.DoesNotExist:  
                    pass  
              
                try:
                    order_product = OrderProduct.objects.filter(Q(product=product) & Q(customer=user_id) & ~Q(item_cancel=True) & ~Q(return_request=True) & Q(order_id__status="Delivered")).first()
                    if order_product is not None:
                        print(order_product.product.variant_name)
                    else:
                        messages.error(request, 'You cant review the product. You have to buy the product to review the book!!!')
                        return redirect('product_detail',id=product_id)
                except OrderProduct.DoesNotExist:
                    messages.error(request,'You cant review the product.You have to buy the product for review the book!!!')
                    return redirect('product_detail',id=product_id)
                review=ProductReview(product=product,rating=rating,text=review_desc,user=user_id,title=title)
                review.save()
                messages.success(request,'Review saved!!!')
                return redirect('product_detail',id=product_id)  
        except Exception as e:
            print(e)
        return redirect('product_detail',id=product_id)    
    else:
        return redirect('user_login')

def user_search(request):

    try:
        context={}
        if request.method=="POST":
            query=request.POST.get('searchquery')
            category=Category.objects.all().order_by('id')
            search_result = Product_variant.objects.filter(
            Q(product__product_title__icontains=query) | Q(author__author_name__icontains=query) | Q(edition__editons_name__icontains=query),
            product__is_active=True,  
            is_active=True )
            print(search_result)
            context={'listproducts':search_result,
                     'category':category}
            return render(request,'user/user_search.html',context)

            
    except Exception as e:
        print(e)
        messages.error(request,'Search Failed')
        return redirect('user_search')    


    return render(request,'user/user_search.html',context)

def search_suggestions(request):
    try:
        if request.method == "GET":
            query = request.GET.get('query', '')
            suggestions = []
            if query:
                # Query your database for relevant suggestions based on the input query
                products = Products.objects.filter(product_title__icontains=query)[:5]
                if products:
                    suggestions = [product.product_title for product in products]
                author = Author.objects.filter(author_name__icontains=query)[:5] 
                if author:
                    suggestions= [author.author_name for author in author]            
            
            return JsonResponse({'suggestions': suggestions})
        elif request.method == "POST":
            query = request.POST.get('searchquery', '')
            print(query)
            category = Category.objects.all().order_by('id')
            search_result = Product_variant.objects.filter(
                Q(product__product_title__icontains=query) |
                Q(author__author_name__icontains=query) |
                Q(edition__editons_name__icontains=query),
                product__is_active=True,
                is_active=True
            )
            context = {
                'listproducts': search_result,
                'category': category
            }
            return render(request, 'user/browse_products.html', context)
    except Exception as e:
        print(e)


def category_wise(request,id):
    try:
       
        category = Category.objects.get(id=id)
        category_list=Category.objects.filter(is_active=True).order_by('id')
        product=Product_variant.objects.filter(category=category, is_active=True)
        categoryall = Category.objects.filter(product_variant__is_active=True).distinct().order_by('-id')
        context={'listproducts':product,'category':categoryall,'categoryname':category,'category_list':category_list}
        return render(request,'user/category_wise.html',context)
    except Exception as e:
        print(e)
        messages.error(request,"Category wise pick failed")
        return redirect('index')        


def user_profile(request):
    try:
        user=CustomUser.objects.get(id=request.user.id)
        address=UserAddress.objects.filter(user=user)
        orders = Order.objects.filter(user=user).order_by('-id')
        category=Category.objects.all().order_by('id')
        context={}
        if request.method=="POST":
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')
            phone=request.POST.get('phone')
            email=request.POST.get('email')
           
            if(user.first_name!=first_name):
                user.first_name=first_name
            if(user.last_name!=last_name):
                user.last_name=last_name
            if(user.phone!=phone):
                user.phone=phone

            user.save()
            messages.success(request,"User Updated Successfully")
            return redirect('user_profile')
      
        context={'orders':orders,'address':address,'category':category}
    except Exception as e:
        print(e)
        messages.error(request,"user not found!!")    
    return render(request,'user/user_profile.html',context)

def change_email(request,id):
    try:
        user=CustomUser.objects.get(id=id)
        

        context={}

        context={'user':user}
        if request.method=="POST":
            email=request.POST.get('email')
            if user.email != email:
                otp=get_random_string(length=6, allowed_chars='1234567890')
                user.otp=otp

                send_otp_email(email,otp)

                user.email=email

                user.save()

                request.session['old_email']=user.email
                return redirect('otp_verification_edit',user_id=user.id)


        return render(request,'change_email.html',context)
    except Exception as e:
        print(e)


@cache_control(no_cache=True, no_store=True) 
def change_password_user(request,id):
    if 'custom_user_id' in request.session:
        return redirect('admin_dashboard')
    
    context={}

    try:
        
       
        user=CustomUser.objects.get(id=id)
        context={'user':user}
        print(user)
        if user is None:
            messages.error(request,"No user Found")
            return redirect("user_profile")

        current_pass=request.POST.get('currentpassword')
        newpassword=request.POST.get('password')
        c_password=request.POST.get('c_password')

        

        if not check_password(current_pass, user.password):
            messages.error(request, "Current password does not match")
            return redirect("user_profile")

        if newpassword == current_pass:
            messages.error(request,"Use new password")
            return redirect("user_profile")
        
        if newpassword == c_password:
            

            

            user.set_password(newpassword)
            user.save()
            messages.success(request,"Password successfully changed.Login again!!")
            logout(request)
            return redirect('user_login')
        else:
            messages.error(request,"Password doesnt match")
            return redirect("user_profile")
    except Exception as e:
        print(e)   
        messages.error(request,"Error Updating Password")
        return redirect(f"user_profile") 
    
def add_address(request,id):
    if 'custom_user_id' in request.session:
        return redirect('admin_dashboard')
    try:
        if 'user' in request.session:
            user = request.user
        else:
            messages.error(request,'You need to login first!')
            return redirect('user_login')    
        if request.method == 'POST':
            name = request.POST['name']
            if len(request.POST['phone']) == 10:
                phone = request.POST['phone']
            else:
                messages.error(request,'Enter Valid Mobile Number!')
                return redirect('add_address')    
            address = request.POST['address']
            town = request.POST['town']
            zip = request.POST['zipcode']
            location = request.POST['nearby_location']
            district = request.POST['district']
            state = request.POST['state']
            if not name:
                name = user.first_name


            user_address = UserAddress(user=user, name=name, alternative_mobile=phone, address=address, town=town,
                                       zip_code=zip, nearby_location=location, district=district,state=state )
            user_address.save()
            context={'user':user}
            if id == 1:
                messages.success(request, "Address created.")
                return redirect('place_order',id=user_address.id)
            else:
                messages.success(request, "New address added.")
                return redirect('user_profile')
    except Exception as e:
        print(e)
    return render(request, 'user/add_address.html')

@login_required(login_url='user_login')
def edit_address(request,id,page_id):
    try:
        if 'user' in request.session:
            user = request.user
        else:
            messages.error(request,'You need to login first!')
            return redirect('user_login') 
        addressUser=UserAddress.objects.get(id=id)
        context={}
        context={'addressuser':addressUser,'user':user}
        
        if request.method=='POST':
            name = request.POST['name']
            if len(request.POST['phone']) == 10:
                phone = request.POST['phone']
            else:
                messages.error(request,'Enter Valid Mobile Number!')
                return redirect('edit_address')    
            address = request.POST['address']
            town = request.POST['town']
            zip = request.POST['zipcode']
            location = request.POST['nearby_location']
            district = request.POST['district']
            state = request.POST['state']
            if not name:
                name = user.first_name
            addressUser.name=name
            addressUser.alternative_mobile =phone
            addressUser.address=address
            addressUser.town=town
            addressUser.zip_code=zip
            addressUser.nearby_location=location
            addressUser.district=district
            addressUser.state=state

            addressUser.save()
            if page_id=='0':
                messages.success(request, "Edit Success")
                # return render(request,'user/user_profile.html',context) 
                return redirect('user_profile')
            else:
                messages.success(request, "Edit Success")
                return redirect('place_order',id=addressUser.id)



    except Exception as e:
        print(e)
        messages.error(request, "Edit Address error")
        return render(request,'user/user_profile.html',context)    
    return render(request,'user/edit_address.html',context)

@login_required(login_url='user_login')
def delete_address(request,id):
    try:
        if 'user' in request.session:
            user = request.user
        else:
            messages.error(request,'You need to login first!')
            return redirect('user_login') 
        if id!=0:
            addressUser=UserAddress.objects.get(id=id)
            context={'user':user}
            addressUser.delete()
            messages.success(request, "Delete Success")
            # return render(request,'user/user_profile.html',context) 
            return redirect('user_profile')
        else:
            return render(request,'user/user_profile.html',context) 
    except Exception as e:
        print(e)
        messages.error(request, "Delete Address error")
        return render(request,'user/user_profile.html',context)    
    
@login_required(login_url='user_login')
def order_summary(request,id):
    context = {}
    try:
        if 'user' in request.session:
            my_user = request.user
            order_obj=Order.objects.get(id=id)
            orders = OrderProduct.objects.filter(Q(customer=my_user) and Q(order_id=order_obj)).order_by('-order_id')
            print(orders)
           
            context = {
                'orders': orders, 'order_obj':order_obj
            }
    except Exception as e:
        print(e)
        return redirect('user_profile')

    return render(request,'user/orders.html',context)    
 
@login_required(login_url='user_login')
def view_wallet(request):
    try:
        context = {}
        if 'user' in request.session:
            user = request.user
            try:
                reports = WalletBook.objects.filter(customer=user.id).order_by('-id')
                context = {
                    'reports': reports,
                }
                return render(request, "user/wallet_book.html", context)
            except Exception as e:
                print(e)
                return redirect('user_profile')
        return redirect('index')
    except Exception as e:
        print(e)        


def proceed_to_pay(request):
    user = request.user
    amount_paise = Decimal('0')

    # Check if the amount is passed as a query parameter
    if 'amount' in request.GET:
        razorpay_id=request.GET.get('razor_id')
        if razorpay_id:
            amount=request.GET.get('amount')
            user.wallet += Decimal(amount)
            user.save()
            wallet_acc = WalletBook()
            wallet_acc.customer = user
            wallet_acc.amount = amount
            wallet_acc.description = "Added Money to wallet"
            wallet_acc.increment = True
            wallet_acc.save()
            wallet_url = reverse('view_wallet')
            message = format_html("Amount Rs.{} added to the wallet!!. Check wallet balance: <a href='{}'>{}</a>", amount, wallet_url, 'Go to account statement')
            messages.success(request, message)
            return redirect('user_profile')
        else:
            messages.error(request,"Payment request failed!check internet connection!")
            return redirect('user_profile')



    context = {
        'user': user,
        'amount_paise': amount_paise,  # Pass the amount in paise to the template
    }
    return render(request,'user/user_profile.html',context)


def contact(request):
    try:
        if request.method=="POST":
            name=request.POST.get('username')
            email=request.POST.get('useremail')
            subject=request.POST.get('subject')
            message=request.POST.get('message')

            subject = f"New message from {name}: {subject}"
            message = f"From: {name}\nEmail: {email}\n\n{message}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [settings.EMAIL_HOST_USER]  
            
        
            send_mail(subject, message, from_email, recipient_list)

            messages.success(request,"Message send successfully")
            return redirect('contact')

    except Exception as e:
        print(e)        
    return render(request,'user/contact.html')
