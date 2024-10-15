# myapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import manage_client
from .views import  edit_services, delete_service, manage_service,service_detail,category
from .views import hair_care_services, services_in_subcategory
from .views import booking_service, booking_confirmation



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
    path('manage_service/', views.manage_service, name='manage_service'),
    path('edit_services/<int:service_id>/', edit_services, name='edit_services'),
    path('delete_service/<int:service_id>/', delete_service, name='delete_service'),
    # path('schedule_interview/', views.schedule_interview, name='schedule_interview'),

    path('client_update/', views.client_update, name='client_update'),
    path('client_profile/', views.client_profile, name='client_profile'),
    path('client_services/', views.client_services, name='client_services'),
    path('hair_care_services/', views.hair_care_services, name='hair_care_services'),
    path('hair_cut_services/', views.hair_cut_services, name='hair_cut_services'),
    path('facial_services/', views.facial_services, name='facial_services'),
    path('all_type_skin/', views.all_type_skin, name='all_type_skin'),
    path('mani-pedi-services/', views.mani_pedi_services, name='mani-pedi-services'),
     path('waxing-services/', views.waxing_services, name='waxing-services'),

    path('toggle-client-status/<int:client_id>/', views.toggle_client_status, name='toggle_client_status'),
    path('toggle-employee-status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    path('employee_profile/', views.employee_profile, name='employee_profile'),
    path('employee_update/', views.employee_update, name='employee_update'),
    path('employee_services/', views.employee_services, name='employee_services'),
    path('toggle_employee_status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    path('toggle_employee_approval/<int:employee_id>/', views.toggle_employee_approval, name='toggle_employee_approval'),
    path('service/<int:service_id>/', service_detail, name='service_detail'),
    path('category/', views.category, name='category'),
    path('booking_service/<int:service_id>/', booking_service, name='booking_service'),
    path('booking_confirmation/', booking_confirmation, name='booking_confirmation'),

    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    # path('subcategory/edit/<int:subcategory_id>/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategory/delete/<int:subcategory_id>/', views.delete_subcategory, name='delete_subcategory'),
    path('edit-subcategory/<int:subcategory_id>/', views.edit_subcategory, name='edit_subcategory'),
    path('hair-care/<int:subcategory_id>/', services_in_subcategory, name='services_in_subcategory'),
    

    path('schedule-interview/', views.schedule_interview, name='schedule_interview'),
]

    

   
    

   
   
    

    



