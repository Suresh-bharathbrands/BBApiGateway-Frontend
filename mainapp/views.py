from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from mainapp.forms import *
from mainapp.api_call import call_get_method,call_post_method,call_post_method_for_without_token, call_put_method
import requests


# Create your views here.
BASE_URL = 'http://dummy.pythonanywhere.com/'

def dashboard(request):
    return render(request,'dashboard.html')
def page1(request):
    return render(request,'page1.html')

# def m_dashboard(request):
#     endpoint_url = f"https://bbv5cb.pythonanywhere.com/get-group-by-user-id/{request.session.get('user_id')}"
#     response = requests.get(endpoint_url)
#     if response.status_code == 200:
#         groups_data = response.json()
#         next_url = request.GET.get('next')  
#         print(next_url)
#         group_response = call_get_method(BASE_URL, 'group', access_token=request.session.get('Token'))
#         if group_response.status_code == 200:
#             groups = group_response.json()
           
#         else:
#             groups = []

#     context = {
#         'm_dashboard': 'active',
#         'groups_data': groups_data,
#         'next_url': next_url, 
#         'groups': groups,
#     }
#     return render(request,'Member/m_dashboard.html',context)