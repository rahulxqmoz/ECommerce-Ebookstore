from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.shortcuts import redirect, render
from user_app.models import CustomUser
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate,login,logout

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

                user = CustomUser.objects.create(first_name=user_data['first_name'],password=user_data['password'], phone=user_data['phonenumber'],last_name=user_data['last_name'],email=user_data['email'])    
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

def regenerate_otp(request):
    return redirect(request,'otp_verification')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,email=email, password=password)
        print(user)
        
           
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



def user_logout(request):
    logout(request)
    return redirect('index')