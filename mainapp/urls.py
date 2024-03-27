from django.urls import path,include
from mainapp import views
urlpatterns=[
    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.SignIn,name='SignIn'),
    path('logout/', views.Logout, name='logout'),
    path('page1',views.page1,name='page1'),
    path('channel',views.channel,name='channel'),
    path('channel_edit/<channel_id>/', views.channel_edit, name='channel_edit'),
    path('channel_delete/<channel_id>/', views.channel_delete, name='channel_delete'),
    path('service_category_master',views.service_category_master,name='service_category_master'),
    path('service_category_master_edit/<service_category_id>/',views.service_category_master_edit,name='service_category_master_edit'),
    path('service_category_master_delete/<service_category_id>/',views.service_category_master_delete,name='service_category_master_delete'),
    path('service',views.service,name='service'),
    path('service_edit/<service_id>/', views.service_edit, name='service_edit'),
    path('api_parameter',views.api_parameter,name='api_parameter'),
    path('api_parameter_edit/<parameter_id>/', views.api_parameter_edit, name='api_parameter_edit'),
    path('process',views.process_data_submission,name='process'),
    path('service_orchestration/',views.service_orchestration,name='service_orchestration'),
    path('process_edit/<process_id>/', views.process_edit, name='process_edit'),
    path('serviceplan',views.serviceplan,name='serviceplan'),
    path('serviceplan_edit/<serivce_plan_id>/', views.serviceplan_edit, name='serviceplan_edit'),
    path('api_registration',views.api_registration,name='api_registration'),
    path('api_registration_edit/<API_id>/', views.api_registration_edit, name='api_registration_edit'),
    path('output_consolidation/', views.output_consolidation, name='output_consolidation'),
    path('output_consolidation_save/', views.output_consolidation_save, name='output_consolidation_save'),
    path('micro_service_registration/', views.micro_service_registration, name='micro_service_registration'),
    path('bulk_delete/', views.bulk_delete, name='bulk_delete'),

]

