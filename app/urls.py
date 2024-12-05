from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name="home"),
    path('profile/', views.profile,name="profile"),
    path('category/', views.category,name="category"),
    path('detail/', views.detail,name="detail"),
    path('search/', views.search,name="search"),
    path('register/', views.register,name="register"),
    path('login/', views.loginPage,name="login"),
    path('logout/',views.logoutPage,name="logout"),
    path('cart/',views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('checkoutsuccess/',views.checkoutsuccess,name="checkoutsuccess"),
    path('update_item/',views.updateItem,name="update_item"),
    path('gioi_thieu/', views.gioi_thieu, name='gioi_thieu'),
    path('contact/', views.contact, name='contact'),


    
    #payment
    path('pay', views.index, name='index'),
    path('payment', views.payment, name='payment'),
    path('payment_ipn', views.payment_ipn, name='payment_ipn'),
    path('payment_return', views.payment_return, name='payment_return'),
    path('query', views.query, name='query'),
    path('refund',views.refund, name='refund'),


    path('revenue-report', views.revenue_report, name='revenue_report'),
    path('revenue-report-month', views.revenue_report_month, name='revenue_report_month'),
    path('quantity', views.quantity, name='quantity'),
    path('kho', views.kho, name='kho'),


]
