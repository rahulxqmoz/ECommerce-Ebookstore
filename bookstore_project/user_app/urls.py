from . import views


from django.urls import path


urlpatterns = [
 
    path('', views.index,name="index"),
    path('user_sign_up/', views.user_sign_up,name="user_sign_up"),
    path('user_login/', views.user_login,name="user_login"),
    path('otp_verification/<int:user_id>/', views.otp_verification,name="otp_verification"),
    path('cancel_registration/<int:user_id>/', views.cancel_registration,name="cancel_registration"),
    path('regenerate_otp/<int:user_id>/', views.regenerate_otp,name="regenerate_otp"),
    path('user_log_out/', views.user_logout,name="user_logout"),
    path('forgot-password/', views.user_forgotpassword, name="forgot_password"),
    path('reset-password/<token>/', views.change_password, name="reset_password"),

    path('product_detail/<int:id>/', views.product_detail, name="product_detail"),
    path('browse_products/', views.browse_products, name="browse_products"),

    path('write_review/', views.write_review, name="write_review"),
    
    path('user_search/', views.user_search, name="user_search"),
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('category_wise/<int:id>/', views.category_wise, name="category_wise"),

    path('user_profile/', views.user_profile, name="user_profile"),
    path('change_email/<int:id>/', views.change_email, name="change_email"),
    path('change_password/<int:id>/', views.change_password_user, name="change_password_user"),
    path('add_address/<int:id>/', views.add_address, name="add_address"),
    path('edit_address/<int:id>/<int:page_id>/', views.edit_address, name="edit_address"),
    path('delete_address/<int:id>/', views.delete_address, name="delete_address"),

    path('order_summary/<int:id>/', views.order_summary, name="order_summary"),
    path('proceed_to_pay/', views.proceed_to_pay, name="proceed_to_pay"),
    path('view_wallet/', views.view_wallet, name="view_wallet"),
    path('contact/', views.contact, name="contact"),
   
]
