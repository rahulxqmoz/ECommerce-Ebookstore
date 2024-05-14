from . import views


from django.urls import path


urlpatterns = [
    path('cancel_order/<int:id>/',views.cancel_order,name='cancel_order'),
    path('order-return/<int:order_id>/', views.order_return, name="order_return"),
    path('pdf_view/<int:order_id>/', views.ViewOrderInvoice.as_view(), name="pdf_view"),
    path('pdf_download/<int:order_id>/', views.DownloadPDF.as_view(), name="pdf_download"),
    path('test_invoice/<int:order_id>/', views.test_invoice, name="test_invoice"),
    
]