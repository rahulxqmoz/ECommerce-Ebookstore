from . import views


from django.urls import path


urlpatterns = [
    
    path('add-wish-list/<int:id>/',views.add_wish_list,name='add_wishlist'),
    path('wish-list',views.view_wishlist,name='view_wishlist'),
    path('delete-wishlist/<int:id>/',views.delete_wish_list,name='delete_wishlist')
   
]
