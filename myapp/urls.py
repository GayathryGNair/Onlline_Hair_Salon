# myapp/urls.py

from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import manage_client
from .views import  edit_services, delete_service, manage_service,service_detail,category
from .views import for_women_services
from .views import (
    manage_men_category,
    edit_men_category,
    delete_men_category,
    edit_men_subcategory,
    delete_men_subcategory,
)
from .views import (
    manage_men_service,
    # other views...
)
from .views import (
    manage_men_service,
    edit_men_service,
    delete_men_service,
    # other views...
)






urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('gallery', views.gallery, name='gallery'),
    path('blog', views.blog, name='blog'),
    path('contact', views.contact, name='contact'),

    path('oauth/', include('social_django.urls', namespace='social')),
    path('social/', include('social_django.urls', namespace='social')),
  
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
    path('employee_registeration', views.employee_registeration, name='employee_registeration'),
    # path('employee/update-profile/', views.update_employee_profile, name='update_employee_profile'),
    path('client_update/', views.client_update, name='client_update'),
    path('client_profile/', views.client_profile, name='client_profile'),
    path('client_services/', views.client_services, name='client_services'),
    

    path('toggle-client-status/<int:client_id>/', views.toggle_client_status, name='toggle_client_status'),
    path('toggle-employee-status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    path('employee_profile/', views.employee_profile, name='employee_profile'),
    path('employee_update/', views.employee_update, name='employee_update'),
    path('employee_services/', views.employee_services, name='employee_services'),
    path('toggle_employee_status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    path('toggle_employee_approval/<int:employee_id>/', views.toggle_employee_approval, name='toggle_employee_approval'),
    path('service/<int:service_id>/', service_detail, name='service_detail'),
    path('category/', views.category, name='category'),
    path('search/', views.search_services, name='search_services'),

    path('booking/<int:service_id>/', views.booking_service, name='booking_service'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
   

    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    # path('subcategory/edit/<int:subcategory_id>/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategory/delete/<int:subcategory_id>/', views.delete_subcategory, name='delete_subcategory'),
    path('edit-subcategory/<int:subcategory_id>/', views.edit_subcategory, name='edit_subcategory'),
    path('billing/<int:booking_id>/', views.billing, name='billing'),  

    

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('employee/manage-service/', views.employee_manage_service, name='employee_manage_service'),
    # path('employee/edit-service/<int:service_id>/', views.employee_edit_service, name='employee_edit_service'),
    # path('employee/category/', views.employee_category, name='employee_category'),
    path('employee/view-appointments/', views.view_appointments, name='view_appointments'),
    path('add_feedback/<int:booking_id>/', views.add_feedback, name='add_feedback'),
    path('view_feedback/<int:booking_id>/', views.view_feedback, name='view_feedback'),
    path('client_bookings/', views.client_bookings, name='client_bookings'),
    path('current-bookings/', views.client_current_bookings, name='client_current_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    path('client/service-history/', views.service_history, name='service_history'),

    path('current-bookings/', views.client_current_bookings, name='client_current_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('view-feedback/', views.employee_view_feedback, name='employee_view_feedback'),

    path('employee_bookings/', views.employee_bookings, name='employee_bookings'),

    # path('client/payments/', views.payments, name='payments'),
    path('client/payments/pay/<int:booking_id>/', views.pay_now, name='pay_now'),
    path('client/payments/razorpay/<int:booking_id>/', views.razorpay_payment, name='razorpay_payment'), 

    path('send-bill/<int:booking_id>/', views.send_bill, name='send_bill'),
    path('payments/', views.view_payments, name='view_payments'),
    path('update-payment-status/<int:payment_id>/', views.update_payment_status, name='update_payment_status'),
    path('confirm_payment/<str:transaction_id>/', views.confirm_payment, name='confirm_payment'),

    
    path('client/payments/razorpay/<int:booking_id>/', views.razorpay_payment, name='razorpay_payment'),
   
    path('men_services/', views.men_services, name='men_services'),  # URL for Men's services
    path('women_services/', views.women_services, name='women_services'),

    path('forwomen-services/', for_women_services, name='forwomen_services'),
    path('formen-services/', views.for_men_services, name='formen_services'),
    
    path('client_women-services/', views.client_women_services, name='client_women_services'),
     path('client_men-services/', views.client_men_services, name='client_men_services'),




################################################################################


    path('manage-men-category/', views.manage_men_category, name='manage_men_category'),
    path('manage-men-category/', manage_men_category, name='manage_men_category'),
    path('edit-men-category/<int:category_id>/', edit_men_category, name='edit_men_category'),
    path('delete-men-category/<int:category_id>/', delete_men_category, name='delete_men_category'),

    # Male Subcategory Management
    path('edit-men-subcategory/<int:subcategory_id>/', edit_men_subcategory, name='edit_men_subcategory'),
    path('delete-men-subcategory/<int:subcategory_id>/', delete_men_subcategory, name='delete_men_subcategory'),

    path('manage-men-service/', manage_men_service, name='manage_men_service'),
    path('edit-men-service/<int:service_id>/', edit_men_service, name='edit_men_service'),
    path('delete-men-service/<int:service_id>/', delete_men_service, name='delete_men_service'),


    path('api/chatbot/', views.chatbot_response, name='chatbot_response'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('offers/add/', views.add_offer, name='add_offer'),
    path('offers/', views.offer_list, name='offer_list'),
]

   

   

   


    

   
    

   
   
    

    



