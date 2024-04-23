from . import views


from django.urls import path


urlpatterns = [
 
    path('', views.admin_login,name="admin_login"),
    path('admin_dashboard/', views.admin_dashboard,name='admin_dashboard'),
    path('admin_logout/', views.admin_logout,name='admin_logout'),
    path('admin_user/', views.admin_user,name='admin_users'),
    path('admin_user_manage/<int:id>/', views.admin_user_manage,name='admin_user_manage'),

    path('admin_category/', views.admin_category,name='admin_category'),
    path('admin_category_view/', views.admin_category_view,name='admin_category_view'),
    path('admin_edit_category/<int:id>', views.admin_edit_category,name='admin_edit_category'),
    path('admin_delete_category/<int:id>', views.admin_delete_category,name='admin_delete_category'),

    path('admin_author/', views.admin_author,name='admin_author'),
    path('admin_edit_author/<int:id>', views.admin_edit_author,name='admin_edit_author'),
    path('admin_add_author/', views.admin_add_author,name='admin_add_author'),
    path('admin_delete_author/<int:id>', views.admin_delete_author,name='admin_delete_author'),

    path('admin_add_offer/', views.admin_add_offer,name='admin_add_offer'),
    path('admin_offer/', views.admin_offer,name='admin_offer'),
    path('admin_delete_offer/<int:id>', views.admin_delete_offer,name='admin_delete_offer'),
    path('admin_edit_offer/<int:id>', views.admin_edit_offer,name='admin_edit_offer'),

    path('admin_add_product/', views.admin_add_product,name='admin_add_product'),
    path('admin_product/', views.admin_product,name='admin_product'),
    path('admin_product_edit/<int:id>', views.admin_product_edit,name='admin_product_edit'),
    path('admin_product_delete/<int:id>', views.admin_product_delete,name='admin_product_delete'),

    path('admin_add_edition/', views.admin_add_edition,name='admin_add_edition'),
    path('admin_edition/', views.admin_edition,name='admin_edition'),
    path('admin_edit_edition/<int:id>', views.admin_edit_edition,name='admin_edit_edition'),
    path('admin_delete_edition/<int:id>', views.admin_delete_edition,name='admin_delete_edition'),

    path('admin_add_product_variant/', views.add_product_variant,name='admin_add_product_variant'),
    path('admin_productvariant/', views.admin_productvariant,name='admin_productvariant'),
    path('admin_edit_variant/<int:id>', views.admin_edit_variant,name='admin_edit_variant'),
    path('admin_delete_variant/<int:id>', views.admin_delete_variant,name='admin_delete_variant'),
    path('delete_image/<int:image_id>', views.delete_image,name='delete_image'),

    path('admin_add_coupon/', views.admin_add_coupon,name='admin_add_coupon'),
    path('admin_coupon/', views.admin_coupon,name='admin_coupon'),
    path('admin_delete_coupon/<int:id>', views.admin_delete_coupon,name='admin_delete_coupon'),
    path('admin_edit_coupon/<int:id>', views.admin_edit_coupon,name='admin_edit_coupon'),

    path('admin_order/', views.admin_order,name='admin_order'),
    path('admin_order_update/<int:id>', views.admin_order_update,name='admin_order_update'),
    
]