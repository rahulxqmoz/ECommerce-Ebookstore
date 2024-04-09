import uuid
from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.shortcuts import redirect, render
from user_app.models import CustomUser,Forgotpassword
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
# Create your views here.

def index(request):
    return render(request,'user/index.html')

def user_sign_up(request):
    if request.method=="POST":
        
        field_names = ['first_name', 'last_name', 'email', 'phonenumber', 'password', 'c_passsword',
                           'referral_code']
        user_data = {field: request.POST.get(field, '') for field in field_names}

        exist_email = CustomUser.objects.filter(email=user_data['email'])
        exist_phone = CustomUser.objects.filter(phone=user_data['phonenumber'])

      


        if exist_email:
            messages.error(request,"Email already exists")
        elif exist_phone:
            messages.error(request,"phone number already exists")
        else:
            if (user_data['password']==user_data['c_passsword']):
                hashed_password = make_password(user_data['password'])

                user = CustomUser.objects.create(first_name=user_data['first_name'],password=hashed_password, phone=user_data['phonenumber'],last_name=user_data['last_name'],email=user_data['email'])    
                otp = get_random_string(length=6, allowed_chars='1234567890')

                user.otp=otp
                user.save()

                
                send_otp_email(user_data['email'],otp)
               
                return redirect('otp_verification',user_id=user.id)
            else:
                messages.error(request,"Could not save user")




        
    return render(request,'user/signup.html')

@cache_control(no_store=True, no_cache=True)
def otp_verification(request,user_id):

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
                    messages.success(request, "Account verified.")
                    return redirect('user_login')
                else:
                    messages.error(request, 'Invalid OTP.')
                    return redirect('otp_verification', user.id)
            else:
                messages.error(request, "Invalid OTP")
                return redirect('otp_verification', user.id)


    except Exception as e:
        print(e)        

    return render(request,"user/otp_verification.html",context)

cache_control(no_store=True, no_cache=True)
def regenerate_otp(request,user_id):
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
    

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,email=email, password=password)
        if user is not None and  user.is_superuser==False:
                login(request, user)
                return redirect('index')
        else:
                messages.error(request, 'Invalid email or password')
       
    return render(request, 'user/login.html')


    # if request.method=="POST":
    #     email=request.POST["email"]
    #     password=request.POST["password"]
        
    #     user=authenticate(request,email=email,password=password)

       
        
    #     try:

    #         if user:
    #             if user.is_verified and user.is_superuser == False:
    #                 login(request,user)
    #                 request.session['user'] = email
    #                 messages.success(request, "logged in successfully")
    #                 return redirect('index')
    #             else:
    #                 if not user.is_verified:
    #                     messages.success(request, "Verify your account.")
    #                     return redirect('otp_verification', user.id)
    #                 messages.error(request, "invalid credentials.")
    #         else:
    #             messages.error(request, "Invalid credentials.")
    #             return redirect('user_login')
    #     except Exception as e:
    #         print(e)
    # return render(request,'user/login.html')        




def send_otp_email(email, otp):
    subject = 'Your One-Time Password (OTP)'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


# def user_forgotpassword(request):
#     if 'email' in request.session:
#         return redirect('admin_dashboard')
#     try:
#         if request.method == 'POST':
#             email = request.POST.get('email', None)
#             my_user = CustomUser.objects.get(email=email)
#             print(my_user)
#             token = str(uuid.uuid4())
#             print(my_user.id)

#             profile_token = Forgotpassword.objects.get(user=my_user.id)
#             print(profile_token)
#             profile_token.forgot_password_token = token
#             profile_token.save()

#             send_forget_password_mail(email,token)
#             messages.success(request, "Password reset link sent to the email.")
#             return redirect('user_login')

#     except Exception as e:
#         messages.error(request, "User not found")
#         print(e)
#     return render(request, 'user/forgotpassword.html')

def user_forgotpassword(request):
    if 'email' in request.session:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', None)
        if email:
            my_user = CustomUser.objects.filter(email=email).first()
            if my_user:
                token = str(uuid.uuid4())
                # Directly query Forgotpassword using my_user
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

    return render(request, 'user/forgotpassword.html')

def change_password(request,token):
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

                #hashed_password = make_password(newpassword)

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


def user_logout(request):
    logout(request)
    return redirect('index')


def send_forget_password_mail(email, token):
    subject = "Forgot password"
    message = f'Hi, click the link to reset your password http://127.0.0.1:8000/reset-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    send_mail(subject, message, email_from, recipient_list)
    return True

