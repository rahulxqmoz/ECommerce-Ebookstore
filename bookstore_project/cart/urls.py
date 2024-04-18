from . import views


from django.urls import path


urlpatterns = [
    path('add_to_cart/<int:id>', views.add_to_cart,name='add_to_cart'),
    path('view_cart/<int:id>', views.view_cart,name='view_cart'),
    path('delete_cart/<int:id>', views.delete_cart,name='delete_cart'),
    path('cart/update_cart_quantity', views.update_cart_quantity,name='update_cart_quantity'),
    
]