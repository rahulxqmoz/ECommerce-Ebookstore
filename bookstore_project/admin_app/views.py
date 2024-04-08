from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.admin.views.decorators import staff_member_required

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
                return redirect('admin_dashboard')
            else:
                messages.error(request,"You cant access this page with this credentials")    
        else:
            messages.error(request,"Inavlid Credentials")

            



    return render(request,'admin/admin_login.html')

@staff_member_required(login_url="admin_login")
def admin_dashboard(request):
    return render(request,'admin/admin_dashboard.html')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')