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
BASE_URL = 'http://127.0.0.1:8000/api/'

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
            if response.status_code != 200: 
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
        'channels_active':'active',
        'channels':channels,
    }
   
    return render(request,'Master/channel.html',context)

def channel_edit(request, channel_id):
    channel_records_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    if channel_records_response.status_code == 200:
        channel_records = channel_records_response.json()
        print('cc_res',channel_records)
    else:
        channel_records = []
    channel = call_get_method(BASE_URL, f'channel-update/{channel_id}/', access_token=request.session.get('Token'))
    
    if channel.status_code == 200:
        channel_data = channel.json()
    else:
        messages.error(request, 'Failed to retrieve channel data', extra_tags='warning')
        return redirect('channel')  

    if request.method == 'POST':
        form = ChannelForm(request.POST, initial=channel_data) 
        if form.is_valid():
            updated_data = form.cleaned_data
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            print('json_data',json_data)
            response = call_put_method(BASE_URL, f'channel-update/{channel_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('channel') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
    else:
        form = ChannelForm(initial=channel_data)

    context = {
        'form': form,
        'channels_active': 'active',
        'channels': channel_data,
        'channel_records':channel_records,
    }

    return render(request, 'Master/channel_edit.html', context)


def service_category_master(request):
    form = ServiceCategoryMasterForm() 
    service_category_master_response = call_get_method(BASE_URL, 'service-category/', access_token=request.session.get('Token'))
    if service_category_master_response.status_code == 200:
        service_category_masters = service_category_master_response.json()
    else:
        service_category_masters = []

        print('res',service_category_master_response)
    if request.method == 'POST':
        endpoint = 'service-category/'
        form = ServiceCategoryMasterForm(request.POST) 
        if form.is_valid():
            print("Valid")
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('service_category_master')
    else:
        print('errorss',form.errors,form)
    
    context={
        'form': form,
        'service_category_masters_active':'active',
        'service_category_masters':service_category_masters,
    }
   
    return render(request,'Master/service_category_master.html',context  )

def service_category_master_edit(request, service_category_id):
    service_category_master_response = call_get_method(BASE_URL, 'service-category/', access_token=request.session.get('Token'))
    if service_category_master_response.status_code == 200:
        service_category_masters_records = service_category_master_response.json()
        print('cc_res',service_category_masters_records)
    else:
        service_category_masters_records = []

    service_category_master = call_get_method(BASE_URL, f'service-category-update/{service_category_id}/', access_token=request.session.get('Token'))
    if service_category_master.status_code == 200:
        service_category_master_data = service_category_master.json()
    else:
        messages.error(request, 'Failed to retrieve service_category_master data', extra_tags='warning')
        return redirect('service_category_master')  

    if request.method == 'POST':
        form = ServiceCategoryMasterForm(request.POST, initial=service_category_master_data) 
        if form.is_valid():
            updated_data = form.cleaned_data
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            print('json_data',json_data)
            response = call_put_method(BASE_URL, f'service-category-update/{service_category_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('service_category_master') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
    else:
        form = ServiceCategoryMasterForm(initial=service_category_master_data)

    context = {
        'form': form,
        'service_category_masters_active': 'active',
        'service_category_masters_records': service_category_masters_records,
        'service_category_master':service_category_master,
        'service_category_masters':service_category_master_data,
    }

    return render(request, 'Master/service_category_master_edit.html', context)


def service(request):
    form = ServiceForm() 

    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []
        print('out',service_response)
    
    channel_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    if channel_response.status_code == 200:
        channels = channel_response.json()
    else:
        channels = []
#for dropdown
    service_category_response = call_get_method(BASE_URL, 'service-category/', access_token=request.session.get('Token'))
    if service_category_response.status_code == 200:
        service_categorys = service_category_response.json()
    else:
        service_categorys = []

    # out_api_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    # if out_api_response.status_code == 200:
    #     out_apis = out_api_response.json()
    # else:
    #     out_apis = []

    if request.method == 'POST':
        endpoint = 'service/'
        form = ServiceForm(request.POST) 
        if form.is_valid():
            print("Valid")
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 201: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('service')
    else:
        print('errorss',form.errors,form)
    
    context={
        'form': form,
        'service':'active',
        'services':services,
        'channels':channels,
        # 'out_apis':out_apis,
        'service_categorys':service_categorys,
    }
   
    return render(request,'Master/service.html',context)

def service_edit(request, service_id):
    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []
        print('out',service_response)

    channel_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    if channel_response.status_code == 200:
        channels = channel_response.json()
        print('cc_res',channels)
    else:
        channels = []
    
    #for dropdown
    service_category_response = call_get_method(BASE_URL, 'service-category/', access_token=request.session.get('Token'))
    if service_category_response.status_code == 200:
        service_categorys = service_category_response.json()
    else:
        service_categorys = []

    service = call_get_method(BASE_URL, f'service-update/{service_id}/', access_token=request.session.get('Token'))
    if service.status_code == 200:
        service_data = service.json()
    else:
        messages.error(request, 'Failed to retrieve channel data', extra_tags='warning')
        return redirect('service')  

    if request.method == 'POST':
        form = ServiceForm(request.POST, initial=service_data) 
        if form.is_valid():
            updated_data = form.cleaned_data
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            print('json_data',json_data)
            response = call_put_method(BASE_URL, f'service-update/{service_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('service') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
    else:
        form = ServiceForm(initial=service_data)

    context = {
        'form': form,
        'service_active': 'active',
        'services': services,
        'channels':channels,
        
        'service_categorys':service_categorys,
        'service_response':service_response,
    }

    return render(request, 'Master/service_edit.html', context)

def api_parameter(request):
    form = APIParameterForm() 
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
        print('cc_res',api_parameters)
    else:
        api_parameters = []
        
    if request.method == 'POST':
        endpoint = 'api-parameter/'
        form = APIParameterForm(request.POST) 
        if form.is_valid():
            print("Valid")
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('api_parameter')
    else:
        print('errorss',form.errors,form)
    
    context={
         'form': form,
        'api_parameters_active':'active',
        'api_parameters':api_parameters,
    }
   
    return render(request,'Master/api_parameter.html',context)

def api_parameter_edit(request, parameter_id):
    api_parameter_records_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_records_response.status_code == 200:
        api_parameter_records = api_parameter_records_response.json()
        print('cc_res',api_parameter_records)
    else:
        api_parameter_records = []
    api_parameter = call_get_method(BASE_URL, f'api-parameter-update/{parameter_id}/', access_token=request.session.get('Token'))
    
    if api_parameter.status_code == 200:
        api_parameter_data = api_parameter.json()
    else:
        messages.error(request, 'Failed to retrieve api_parameter data', extra_tags='warning')
        return redirect('api_parameter')  

    if request.method == 'POST':
        form = APIParameterForm(request.POST, initial=api_parameter_data) 
        if form.is_valid():
            updated_data = form.cleaned_data
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            print('json_data',json_data)
            response = call_put_method(BASE_URL, f'api-parameter-update/{parameter_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('api_parameter') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
    else:
        form = APIParameterForm(initial=api_parameter_data)

    context = {
        'form': form,
        'api_parameters_active': 'active',
        'api_parameters': api_parameter_data,
        'api_parameter_records':api_parameter_records,
    }

    return render(request, 'Master/api_parameter_edit.html', context)


def q_table(request):
    form = Q_tableForm() 
    q_table_response = call_get_method(BASE_URL, 'Q-table/', access_token=request.session.get('Token'))
    if q_table_response.status_code == 200:
        q_tables = q_table_response.json()
        print('cc_res',q_tables)
    else:
        q_tables = []
        
    if request.method == 'POST':
        endpoint = 'Q-table/'
        form = Q_tableForm(request.POST) 
        if form.is_valid():
            print("Valid")
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('q_table')
    else:
        print('errorss',form.errors,form)
    
    context={
         'form': form,
        'q_tables_active':'active',
        'q_tables':q_tables,
    }
   
    return render(request,'Master/q_table.html',context)


def q_table_edit(request, Q_id):
    q_table_records_response = call_get_method(BASE_URL, 'Q-table/', access_token=request.session.get('Token'))
    if q_table_records_response.status_code == 200:
        q_table_records = q_table_records_response.json()
        print('cc_res',q_table_records)
    else:
        q_table_records = []
    q_table = call_get_method(BASE_URL, f'Q-table-update/{Q_id}/', access_token=request.session.get('Token'))
    
    if q_table.status_code == 200:
        q_table_data = q_table.json()
    else:
        messages.error(request, 'Failed to retrieve q_table data', extra_tags='warning')
        return redirect('q_table')  

    if request.method == 'POST':
        form = Q_tableForm(request.POST, initial=q_table_data) 
        if form.is_valid():
            updated_data = form.cleaned_data
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
            print('json_data',json_data)
            response = call_put_method(BASE_URL, f'api-parameter-update/{Q_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('q_table') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
    else:
        form = Q_tableForm(initial=q_table_data)

    context = {
        'form': form,
        'q_tables_active': 'active',
        'q_tables': q_table_data,
        'q_table_records':q_table_records,
    }

    return render(request, 'Master/q_table_edit.html', context)


def serviceplan(request):
    form = ServicePlanForm() 
    
    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
        print('out',services)
    else:
        services = []

    q_table_records_response = call_get_method(BASE_URL, 'Q-table/', access_token=request.session.get('Token'))
    if q_table_records_response.status_code == 200:
        q_table_records = q_table_records_response.json()
        print('cc_res',q_table_records)
    else:
        q_table_records = []
        
    

    serviceplan_response = call_get_method(BASE_URL, ' service-plan/', access_token=request.session.get('Token'))
    if serviceplan_response.status_code == 200:
        serviceplans = serviceplan_response.json()
        print('cc_res',serviceplans)
    else:
        serviceplans = []
        
    if request.method == 'POST':
        endpoint = ' service-plan/'
        form = ServicePlanForm(request.POST) 
        if form.is_valid():
            print("Valid")
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('serviceplan')
    else:
        print('errorss',form.errors)
    
    context={
         'form': form,
        'serviceplans_active':'active',
        'services':services,
        'serviceplans':serviceplans,
    }
   
    return render(request,'Master/serviceplan.html',context)



def api_registration(request):
    form = ApiRegisterForm() 
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []


    api_registration_response = call_get_method(BASE_URL, 'api-register/', access_token=request.session.get('Token'))
    if api_registration_response.status_code == 200:
        api_registrations = api_registration_response.json()
    else:
        api_registrations = []
        
        
    if request.method == 'POST':
        endpoint = 'api-register/'
        form = ApiRegisterForm(request.POST) 
        if form.is_valid():
            parameter_list=request.POST.getlist('parameter')
            if not isinstance(parameter_list,list):
                parameter_list=[parameter_list]
            json_dataa={
                "API_name":form.cleaned_data['API_name'],
                "Http_verbs":form.cleaned_data['Http_verbs'],
                "base_url":form.cleaned_data['base_url'],
                "end_point":form.cleaned_data['end_point'],
                "parameter":parameter_list
            }
            json_data = json.dumps(json_dataa)
            response = call_post_method(BASE_URL, endpoint, json_data, access_token=request.session.get('Token'))
            if response.status_code != 200:
                messages.error(request, f"Oops..! {response.json()}", extra_tags='warning')
            else:
                messages.success(request, 'Data Saved Successfully', extra_tags='success')
                return redirect('api_registration')
        else:
            print("Errors:", form.errors)
    
    context={
        'form': form,
        'api_registrations_active':'active',
        'api_registrations':api_registrations,
        'api_parameters':api_parameters,
    }
   
    return render(request,'Master/api_registration.html',context)

def api_registration_edit(request, API_id):
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []

    api_registration_records_response = call_get_method(BASE_URL, 'api-register/', access_token=request.session.get('Token'))
    if api_registration_records_response.status_code == 200:
        api_registration_records = api_registration_records_response.json()
        print('cc_res',api_registration_records)
    else:
        api_registration_records = []
    api_registration = call_get_method(BASE_URL, f'api-register-update/{API_id}/', access_token=request.session.get('Token'))
    
    if api_registration.status_code == 200:
        api_registration_data = api_registration.json()
    else:
        messages.error(request, 'Failed to retrieve api_registration data', extra_tags='warning')
        return redirect('api_registration')  

    if request.method == 'POST':
        form = ApiRegisterForm(request.POST, initial=api_registration_data) 
        if form.is_valid():
            parameter_list=request.POST.getlist('parameter')
            if not isinstance(parameter_list,list):
                parameter_list=[parameter_list]
            json_dataa={
                "API_name":form.cleaned_data['API_name'],
                "Http_verbs":form.cleaned_data['Http_verbs'],
                "base_url":form.cleaned_data['base_url'],
                "end_point":form.cleaned_data['end_point'],
                "parameter":parameter_list
            }
            json_data = json.dumps(json_dataa)
            response = call_put_method(BASE_URL, f'api-parameter-update/{API_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('api_registration') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
    else:
        form = ApiRegisterForm(initial=api_registration_data)

    context = {
        'form': form,
        'api_parameters':api_parameters,
        'api_registrations_active': 'active',
        'api_registrations': api_registration_data,
        'api_registration_records':api_registration_records,
    }

    return render(request, 'Master/api_registration_edit.html', context)

def process(request):
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
            if response.status_code != 200: 
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
        'channels_active':'active',
        'channels':channels,
    }
   
    return render(request,'Master/process.html',context)