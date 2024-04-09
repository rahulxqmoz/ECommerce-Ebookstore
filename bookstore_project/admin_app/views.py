from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.admin.views.decorators import staff_member_required

from user_app.models import CustomUser

# Create your views here.

@cache_control(no_cache=True, no_store=True) 
def admin_login(request):
    if request.method=="POST":
        email=request.POST["email"]
        password=request.POST["password"]

        admin = authenticate(email=email,password=password)

        if admin:
            if admin.is_superuser:
                login(request,admin)
                request.session['email'] = email
                return redirect('admin_dashboard')
            else:
                messages.error(request,"You cant access this page with this credentials")    
        else:
            messages.error(request,"Inavlid Credentials")

            



    return render(request,'admin/admin_login.html')

@staff_member_required(login_url="admin_login")
def admin_dashboard(request):
    return render(request,'admin/admin_dashboard.html')

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

def admin_logout(request):
    logout(request)
    return redirect('admin_login')