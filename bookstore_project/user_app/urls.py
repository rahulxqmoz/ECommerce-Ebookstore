from . import views


from django.urls import path


urlpatterns = [
 
    path('', views.index,name="index"),
    path('user_sign_up/', views.user_sign_up,name="user_sign_up"),
    path('user_login/', views.user_login,name="user_login"),
    path('otp_verification/<int:user_id>/', views.otp_verification,name="otp_verification"),
    path('regenerate_otp/<int:user_id>/', views.regenerate_otp,name="regenerate_otp"),
    path('user_log_out/', views.user_logout,name="user_logout"),
    path('forgot-password/', views.user_forgotpassword, name="forgot_password"),
    path('reset-password/<token>/', views.change_password, name="reset_password"),
    path('product_detail/<int:id>/', views.product_detail, name="product_detail"),
    path('browse_products/', views.browse_products, name="browse_products"),
    path('write_review/', views.write_review, name="write_review"),
    path('user_search/', views.user_search, name="user_search"),
]
