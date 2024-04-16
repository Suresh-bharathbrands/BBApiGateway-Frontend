from django.urls import path,include
from mainapp import views
urlpatterns=[
    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.SignIn,name='SignIn'),
    path('logout/', views.Logout, name='logout'),
    path('page1',views.page1,name='page1'),

    path('channel',views.channel,name='channel'),
    path('channel_edit/<channel_id>/', views.channel_edit, name='channel_edit'),
    path('channel_view/<channel_id>/', views.channel_view, name='channel_view'),
    path('channel_delete/<channel_id>/', views.channel_delete, name='channel_delete'),

    path('service_category_master',views.service_category_master,name='service_category_master'),
    path('service_category_master_edit/<service_category_id>/',views.service_category_master_edit,name='service_category_master_edit'),
    path('service_category_master_view/<service_category_id>/',views.service_category_master_view,name='service_category_master_view'),
    path('service_category_master_delete/<service_category_id>/',views.service_category_master_delete,name='service_category_master_delete'),

    path('service',views.service,name='service'),
    path('service_view/<service_id>/', views.service_view, name='service_view'),
    path('service_edit/<service_id>/', views.service_edit, name='service_edit'),
    path('service_delete/<service_id>/', views.service_delete, name='service_delete'),

    path('api_parameter',views.api_parameter,name='api_parameter'),
    path('api_parameter_view/<parameter_id>/', views.api_parameter_view, name='api_parameter_view'),
    path('api_parameter_edit/<parameter_id>/', views.api_parameter_edit, name='api_parameter_edit'),
    path('api_parameter_delete/<parameter_id>/', views.api_parameter_delete, name='api_parameter_delete'),

    path('process',views.process_data_submission,name='process'),
    path('process_view/<process_id>/', views.process_view, name='process_view'),
    path('process_edit/<process_id>/', views.process_edit, name='process_edit'),
    path('process_delete/<process_id>/', views.process_delete, name='process_delete'),

    path('service_orchestration/',views.service_orchestration,name='service_orchestration'),
    path('service_orchestration_edit/<SO_id>/',views.service_orchestration_edit,name='service_orchestration_edit'),
    path('service_orchestration_view/<SO_id>/',views.service_orchestration_view,name='service_orchestration_view'),
    path('service_orchestration_delete/<SO_id>/',views.service_orchestration_delete,name='service_orchestration_delete'),

    path('serviceplan',views.serviceplan,name='serviceplan'),
    path('serviceplan_view/<serivce_plan_id>/', views.serviceplan_view, name='serviceplan_view'),
    path('serviceplan_edit/<serivce_plan_id>/', views.serviceplan_edit, name='serviceplan_edit'),
    path('serviceplan_delete/<serviceplan_id>/', views.serviceplan_delete, name='serviceplan_delete'),

    path('api_registration',views.api_registration,name='api_registration'),
    path('api_registration_view/<API_id>/', views.api_registration_view, name='api_registration_view'),
    path('api_registration_edit/<API_id>/', views.api_registration_edit, name='api_registration_edit'),
    path('api_registration_delete/<api_registration_id>/', views.api_registration_delete, name='api_registration_delete'),

    path('output_consolidation/', views.output_consolidation, name='output_consolidation'),
    path('output_consolidation_save/', views.output_consolidation_save, name='output_consolidation_save'),

    path('micro_service_registration/', views.micro_service_registration, name='micro_service_registration'),
    path('micro_service_registration_view/<micro_service_id>/', views.micro_service_registration_view, name='micro_service_registration_view'),
    path('micro_service_registration_edit/<micro_service_id>/', views.micro_service_registration_edit, name='micro_service_registration_edit'),
    path('micro_service_registration_delete/<micro_service_id>/', views.micro_service_registration_delete, name='micro_service_registration_delete'),
    
    path('bulk_delete/', views.bulk_delete, name='bulk_delete'),

]

