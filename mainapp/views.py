from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from mainapp.forms import *
from mainapp.api_call import call_get_method,call_post_method,call_post_method_for_without_token, call_put_method
import requests
import json
from django.contrib import messages
from django.urls import resolve, reverse
import jwt
from django.contrib.auth import logout


# Create your views here.
BASE_URL = 'http://127.0.0.1:5565/api/'

def Logout(request):
    logout(request)
    return redirect('SignIn')

def token_decode(token):
    try:
        decoded_token = jwt.decode(token, options={'verify_signature': False}, algorithms=['HS256'])
        print("Decoded Token:", decoded_token)
        return decoded_token
    except jwt.ExpiredSignatureError:
        print('Token has expired')
    except jwt.DecodeError:
        print('Token Could Not Be Decoded')

def SignIn(request, next_url=None):
    next_url = request.session.get('next') 
    print(next_url)
    print('next URL for login dash')
    form = SignInForm() 
    if request.method == 'POST':
        form = SignInForm(request.POST)
        endpoint = "token/"
    
        if form.is_valid():
            print("fdgfdgd")
            cleaned_data = form.cleaned_data
            print('Clean_DATA..........',cleaned_data)
            json_data = json.dumps(cleaned_data)
            response = call_post_method_for_without_token(BASE_URL, endpoint, json_data)
            
            if response.status_code != 200:
                form = SignInForm() 
                
                print('Response status code:', response.status_code)
                print('Response JSON:', response.json())
                print('Response detail:', response.json().get('detail'))
                print('Response is not 200')
                messages.error(request, str(response.json().get('detail')), extra_tags='error')
                return render(request, 'Auth/SignIn.html',{'form':form})
            else:
                print('Response JSON:', response.json())
                
                # Set the token
                request.session['Token'] = response.json()['access']
                print(request.session['Token'])
                # Decode the token
                dec_resp = token_decode(response.json()['access'])
                request.session['user_id'] = dec_resp['user_id']
                
                print('User ID:', dec_resp['user_id'])
                if next_url:
                    url = resolve(next_url)
                    print('URL name:', url.url_name)
                    return redirect(url.url_name)
                else:
                    return redirect('channel')  
    if request.user.is_authenticated:
       
        # Display a logout link when the user is signed in
        logout_link = f'<a href="{reverse("logout")}">Logout</a>'
    else:
        
        logout_link = ''

    # Render the template with the logout link (if applicable)
    context = {
        'logout_link': logout_link,
        'form': form,
        # 'show_loader': show_loader,
    }
    
    return render(request, 'Auth/SignIn.html', context)

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

def channel(request):
    form = ChannelForm() 
    channel_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    if channel_response.status_code == 200:
        channels = channel_response.json()
        print('cc_res',channels)
    else:
        channels = []
        
    if request.method == 'POST':
        endpoint = 'channel/'
        form = ChannelForm(request.POST) 
        if form.is_valid():
            print("Valid")
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 201: 
                error_message = response.json()
                error_message = error_message['channel_name'][0]
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('channel')
    else:
        print('errorss',form.errors,form)
    
    context={
         'form': form,
        'channels':'active',
        'channels':channels,
    }
   
    return render(request,'Master/channel.html',context)

def channel_edit(request, channel_id):
    channel_response = call_get_method(BASE_URL, f'channel-update/{channel_id}/', access_token=request.session.get('Token'))

    if channel_response.status_code == 200:
        channel_data = channel_response.json()
        print(channel_data)
    else:
        pass
    if request.method == 'POST':
        endpoint = f'channel-update/{channel_id}/'
        form = ChannelForm(request.POST)
        if form.is_valid():
            Output = form.cleaned_data
            json_data = json.dumps(Output)
            response = call_put_method(BASE_URL, endpoint, json_data, access_token=request.session.get('Token'))

            if response.status_code != 201:
                error_message = response.json()
                messages.error(request, f"Oops..! {response.json()}", extra_tags='warning')
            else:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('channel')
        else:
            print('error................' ,form.errors)
    else:
        form = ChannelForm(initial=channel_data)

    context = {
        'form': form,
        'channels': 'active',
        'channels_data': channel_data,
    }

    return render(request, 'Master/channel_edit.html', context)


def service_category_master(request):
    form = ServiceCategoryMasterForm() 
    service_category_master_response = call_get_method(BASE_URL, 'service-category/', access_token=request.session.get('Token'))

    if service_category_master_response.status_code == 200:
        service_category_masters = service_category_master_response.json()
    else:
        service_category_masters = []
        
    if request.method == 'POST':
        endpoint = 'service-category/'
        form = ServiceCategoryMasterForm(request.POST) 
        if form.is_valid():
            print("Valid")
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 201: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('service_category_master')
    else:
        print('errorss',form.errors,form)
    
    context={
        'form': form,
        'service_category_masters':'active',
        'service_category_masters':service_category_masters,
    }
   
    return render(request,'Master/service_category_master.html',context  )