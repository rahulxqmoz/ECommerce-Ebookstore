from . import views


from django.urls import path


urlpatterns = [
 
    path('', views.admin_login,name="admin_login"),
    path('admin_dashboard/', views.admin_dashboard,name='admin_dashboard'),
    path('admin_logout/', views.admin_logout,name='admin_logout'),
]