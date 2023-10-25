from django.urls import path,include
from mainapp import views
urlpatterns=[
    path('',views.dashboard,name='dashboard'),
    path('SignIn',views.SignIn,name='SignIn'),
    path('logout/', views.Logout, name='logout'),
    path('page1',views.page1,name='page1'),
    path('channel',views.channel,name='channel'),
    path('channel_edit/<channel_id>/', views.channel_edit, name='channel_edit'),
    path('service_category_master',views.service_category_master,name='service_category_master'),
    path('service_category_master_edit/<service_category_id>/',views.service_category_master_edit,name='service_category_master_edit'),
    path('service',views.service,name='service'),
    path('service_edit/<service_id>/', views.service_edit, name='service_edit'),
    path('api_parameter',views.api_parameter,name='api_parameter'),
    path('api_parameter_edit/<parameter_id>/', views.api_parameter_edit, name='api_parameter_edit'),
    path('process',views.process,name='process'),
    path('process_edit/<Q_id>/', views.process_edit, name='process_edit'),
    path('serviceplan',views.serviceplan,name='serviceplan'),
    path('api_registration',views.api_registration,name='api_registration'),
    path('api_registration_edit/<API_id>/', views.api_registration_edit, name='api_registration_edit'),

]
