from django.urls import path,include
from mainapp import views
urlpatterns=[
    path('',views.dashboard,name='dashboard'),
    path('page1',views.page1,name='page1'),

]