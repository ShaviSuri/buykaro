from django.urls import path
from . import views

urlpatterns = [
    path('seller/', views.home, name ="home"),
    path('seller/dashboard/', views.home),
    path('seller/customers/<str:pk_test>', views.customers, name ="customer"),
    path('seller/products/', views.products, name ="product"),
    path('seller/create_order', views.CreateOrder, name ='create_order'),
    path('seller/update_order/<str:pk>', views.UpdateOrder, name ='update_order'),
    path('seller/delete_order/<str:pk>', views.DeleteOrder, name ='delete_order'),
    path('seller/create_user/', views.CreateUser, name ='create_user'),
    path('seller/create_sorder/<str:pk>', views.CreateSorder, name ='create_sorder')
    
    
    
]