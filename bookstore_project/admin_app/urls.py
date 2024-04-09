from . import views


from django.urls import path


urlpatterns = [
 
    path('', views.admin_login,name="admin_login"),
    path('admin_dashboard/', views.admin_dashboard,name='admin_dashboard'),
    path('admin_logout/', views.admin_logout,name='admin_logout'),
    path('admin_user/', views.admin_user,name='admin_users'),
    path('admin_user_manage/<int:id>/', views.admin_user_manage,name='admin_user_manage'),
]