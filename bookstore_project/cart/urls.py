from . import views


from django.urls import path


urlpatterns = [
    path('add_to_cart/<int:id>', views.add_to_cart,name='add_to_cart'),
    path('view_cart/<int:id>', views.view_cart,name='view_cart'),
    path('delete_cart/<int:id>', views.delete_cart,name='delete_cart'),
    path('cart/update_cart_quantity', views.update_cart_quantity,name='update_cart_quantity'),
    path('checkout_address', views.checkout_address,name='checkout_address'),
    path('place_order/<int:id>', views.place_order,name='place_order'),
    path('remove_coupon', views.remove_coupon,name='remove_coupon'),
    path('razorpay-gateway/', views.razorpay_gateway, name='razorpay-gateway'),
    path('callback/', views.callback, name='callback'),
]