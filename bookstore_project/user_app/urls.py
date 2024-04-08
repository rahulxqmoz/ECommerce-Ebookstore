from . import views


from django.urls import path


urlpatterns = [
 
    path('', views.index,name="index"),
    path('user_sign_up/', views.user_sign_up,name="user_sign_up"),
    path('user_login/', views.user_login,name="user_login"),
    path('otp_verification/<int:user_id>/', views.otp_verification,name="otp_verification"),
    path('regenerate_otp/<int:user_id>/', views.regenerate_otp,name="regenerate_otp"),
    path('user_log_out/', views.user_logout,name="user_logout"),
]
