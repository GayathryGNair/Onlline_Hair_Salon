# myapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('gallery', views.gallery, name='gallery'),
    path('blog', views.blog, name='blog'),
    path('contact', views.contact, name='contact'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('for_men', views.for_men, name='for_men'),
    path('for_women', views.for_women, name='for_women'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('Book/', views.Book, name='Book'),
    path('forgot_reset', views.forgot_reset, name='forgot_reset'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('store_dashboard/', views.store_dashboard, name='store_dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    
]
   
    

   
   
    

    



