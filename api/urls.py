from django.urls import path,include
from . import views


urlpatterns = [
    path('customer-details/', views.CustomerDeatilsView.as_view(),name='customer_details'),
    path('otp-verification/', views.OPTView.as_view(),name='otp_api'),
]

