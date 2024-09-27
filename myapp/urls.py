# myapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import manage_client
from .views import delete_service


urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('gallery', views.gallery, name='gallery'),
    path('blog', views.blog, name='blog'),
    path('contact', views.contact, name='contact'),
  
    path('register', views.register, name='register'),
    path('for_men', views.for_men, name='for_men'),
    path('for_women', views.for_women, name='for_women'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('Book/', views.Book, name='Book'),
    path('forgot_reset', views.forgot_reset, name='forgot_reset'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),

    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('user_profile/', views.user_profile, name='user_profile'),

    # path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_client/', views.manage_client, name='manage_client'),
    path('manage_employee/', views.manage_employee, name='manage_employee'),

    path('client_update/', views.client_update, name='client_update'),
    path('client_profile/', views.client_profile, name='client_profile'),
    path('client_services/', views.client_services, name='client_services'),

    path('toggle-client-status/<int:client_id>/', views.toggle_client_status, name='toggle_client_status'),
    path('toggle-employee-status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    path('manage-service/',views.manage_service, name='manage_service'),
    path('delete-service/<int:service_id>/', delete_service, name='delete_service'),
    path('employee_profile/', views.employee_profile, name='employee_profile'),
    path('employee_update/', views.employee_update, name='employee_update'),
    path('employee_services/', views.employee_services, name='employee_services'),
]

    

   
    

   
   
    

    



