from . import views


from django.urls import path


urlpatterns = [
    path('cancel_order/<int:id>/',views.cancel_order,name='cancel_order'),
    path('order-return/<int:order_id>/', views.order_return, name="order_return"),
    
]