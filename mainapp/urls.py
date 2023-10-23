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
   
]
