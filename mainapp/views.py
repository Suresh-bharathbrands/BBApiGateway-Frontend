from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from mainapp.forms import *
from mainapp.api_call import *
import requests
import json
from django.contrib import messages
from django.urls import resolve, reverse
import jwt
from django.contrib.auth import logout
from .decorator import custom_login_required

# Create your views here.
# BASE_URL = 'https://bbapigateway.pythonanywhere.com/api/'
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
    form = SignInForm() 
    if request.method == 'POST':
        form = SignInForm(request.POST)
        endpoint = "token/"
    
        if form.is_valid():
            cleaned_data = form.cleaned_data
            json_data = json.dumps(cleaned_data)
            response = call_post_method_for_without_token(BASE_URL, endpoint, json_data)
            
            if response.status_code != 200:
                form = SignInForm()
                messages.error(request, str(response.json().get('detail')), extra_tags='error')
                return render(request, 'Auth/SignIn.html',{'form':form})
            else:
                # Set the token
                request.session['Token'] = response.json()['access']
                # Decode the token
                dec_resp = token_decode(response.json()['access'])
                request.session['user_id'] = dec_resp['user_id'] 
                
                if next_url:
                    url = resolve(next_url)
                    return redirect(url.url_name)
                else:
                    return redirect('dashboard')  
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

@custom_login_required
def dashboard(request):
    return render(request,'dashboard.html')

@custom_login_required
def page1(request):
    return render(request,'page1.html')


@custom_login_required
def record_get(endpoint,token):
    record_response = call_get_method(BASE_URL, endpoint, token)
    if record_response.status_code == 200:
        records = record_response.json()
    else:
        records = []
    return records



@custom_login_required
def channel(request):
    print('request',request)
    form = ChannelForm()
    channels_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    if channels_response.status_code == 200:
        channels = channels_response.json()
    else:
        channels = []
    if request.method == 'POST':
        endpoint = 'channel/'
        form = ChannelForm(request.POST) 
        if form.is_valid():
            Output = form.cleaned_data
            json_data=json.dumps(Output)

            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200:
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('channel')
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
    
    context={
         'form': form,
        'channels_active':'active',
        'channels':channels,
    }
   
    return render(request,'Master/channel.html',context)

@custom_login_required
def channel_edit(request, channel_id):
    channel_records_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    if channel_records_response.status_code == 200:
        channel_records = channel_records_response.json()
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
            response = call_put_method(BASE_URL, f'channel-update/{channel_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('channel') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, form.errors, extra_tags='warning')
    else:
        form = ChannelForm(initial=channel_data)

    context = {
        'form': form,
        'channels_active': 'active',
        'channels': channel_data,
        'channel_records':channel_records,
    }

    return render(request, 'Master/channel_edit.html', context)



@custom_login_required
def channel_view(request, channel_id):
    channel_records_response = call_get_method(BASE_URL, 'channel/', access_token=request.session.get('Token'))
    if channel_records_response.status_code == 200:
        channel_records = channel_records_response.json()
    else:
        channel_records = []
    channel = call_get_method(BASE_URL, f'channel-update/{channel_id}/', access_token=request.session.get('Token'))
    
    if channel.status_code == 200:
        channel_data = channel.json()
    else:
        messages.error(request, 'Failed to retrieve channel data', extra_tags='warning')
        return redirect('channel')

    
    form = ChannelForm(initial=channel_data)

    context = {
        'form': form,
        'channels_active': 'active',
        'channels': channel_data,
        'channel_records':channel_records,'view':True
    }

    return render(request, 'Master/channel_edit.html', context)

@custom_login_required
def channel_delete(request,channel_id):
    channel = call_delete_method(BASE_URL, f'channel-update/{channel_id}/', access_token=request.session.get('Token'))
    
    if channel.status_code == 200:
        messages.success(request, 'Successfully delete channel data', extra_tags='warning')
    else:
        messages.error(request, 'Failed to delete channel data', extra_tags='warning')
    return redirect('channel')


@custom_login_required
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
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('service_category_master')
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
        
    context={
        'form': form,
        'service_category_masters_active':'active',
        'service_category_masters':service_category_masters,
    }
   
    return render(request,'Master/service_category_master.html',context  )

@custom_login_required
def service_category_master_edit(request, service_category_id):
    service_category_master_response = call_get_method(BASE_URL, 'service-category/', access_token=request.session.get('Token'))
    if service_category_master_response.status_code == 200:
        service_category_masters_records = service_category_master_response.json()
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

@custom_login_required
def service_category_master_view(request, service_category_id):
    service_category_master_response = call_get_method(BASE_URL, 'service-category/', access_token=request.session.get('Token'))
    if service_category_master_response.status_code == 200:
        service_category_masters_records = service_category_master_response.json()
    else:
        service_category_masters_records = []

    service_category_master = call_get_method(BASE_URL, f'service-category-update/{service_category_id}/', access_token=request.session.get('Token'))
    if service_category_master.status_code == 200:
        service_category_master_data = service_category_master.json()
    else:
        messages.error(request, 'Failed to retrieve service_category_master data', extra_tags='warning')
        return redirect('service_category_master')  

    
    form = ServiceCategoryMasterForm(initial=service_category_master_data)

    context = {
        'form': form,
        'service_category_masters_active': 'active',
        'service_category_masters_records': service_category_masters_records,
        'service_category_master':service_category_master,
        'service_category_masters':service_category_master_data,'view':True
    }

    return render(request, 'Master/service_category_master_edit.html', context)

@custom_login_required
def service_category_master_delete(request,service_category_id):
    service_category_master = call_delete_method(BASE_URL, f'service-category-update/{service_category_id}/', access_token=request.session.get('Token'))
    print('service_category_master',service_category_master)
    if service_category_master.status_code == 200:
        messages.success(request, 'Successfully delete service_category_master data', extra_tags='success')
    else:
        messages.error(request, 'Failed to delete service_category_master data', extra_tags='warning')
    return redirect('service_category_master')



@custom_login_required
def service(request):
    form = ServiceForm() 

    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []
       
    
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

    out_api_response = call_get_method(BASE_URL, 'api-register/', access_token=request.session.get('Token'))
    if out_api_response.status_code == 200:
        out_apis = out_api_response.json()
    else:
        out_apis = []

    out_micro_service_response = call_get_method(BASE_URL, 'micro-service-registration/', access_token=request.session.get('Token'))
    if out_micro_service_response.status_code == 200:
        out_micro_services = out_micro_service_response.json()
    else:
        out_micro_services = []

    if request.method == 'POST':
        endpoint = 'service/'
        form = ServiceForm(request.POST) 
        if form.is_valid():
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('service')
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
        
    context={
        'form': form,
        'service_active':'active',
        'services':services,
        'channels':channels,
        'out_apis':out_apis,
        'service_categorys':service_categorys,
        'out_micro_services':out_micro_services
    }
   
    return render(request,'Master/service.html',context)

@custom_login_required
def service_edit(request, service_id):
    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []

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

    out_api_response = call_get_method(BASE_URL, 'api-register/', access_token=request.session.get('Token'))
    if out_api_response.status_code == 200:
        out_apis = out_api_response.json()
    else:
        out_apis = []

    service = call_get_method(BASE_URL, f'service-update/{service_id}/', access_token=request.session.get('Token'))
    if service.status_code == 200:
        service_data = service.json()
    else:
        messages.error(request, 'Failed to retrieve channel data', extra_tags='warning')
        return redirect('service')  


    out_micro_service_response = call_get_method(BASE_URL, 'micro-service-registration/', access_token=request.session.get('Token'))
    if out_micro_service_response.status_code == 200:
        out_micro_services = out_micro_service_response.json()
    else:
        out_micro_services = []


    if request.method == 'POST':
        form = ServiceForm(request.POST, initial=service_data) 
        if form.is_valid():
            updated_data = form.cleaned_data
            # Serialize the updated data as JSON
            json_data = json.dumps(updated_data)
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
    print('service_data',service_data)
    context = {
        'form': form,
        'service_active': 'active',
        'out_apis':out_apis,
        'services': services,
        'channels':channels,
        'service_categorys':service_categorys,
        'service_response':service_response,
        'out_micro_services':out_micro_services,
        'service_data':service_data
    }

    return render(request, 'Master/service_edit.html', context)


@custom_login_required
def service_view(request, service_id):
    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []

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

    out_api_response = call_get_method(BASE_URL, 'api-register/', access_token=request.session.get('Token'))
    if out_api_response.status_code == 200:
        out_apis = out_api_response.json()
    else:
        out_apis = []

    service = call_get_method(BASE_URL, f'service-update/{service_id}/', access_token=request.session.get('Token'))
    if service.status_code == 200:
        service_data = service.json()
    else:
        messages.error(request, 'Failed to retrieve channel data', extra_tags='warning')
        return redirect('service')  


    out_micro_service_response = call_get_method(BASE_URL, 'micro-service-registration/', access_token=request.session.get('Token'))
    if out_micro_service_response.status_code == 200:
        out_micro_services = out_micro_service_response.json()
    else:
        out_micro_services = []


    form = ServiceForm(initial=service_data)
    context = {
        'form': form,
        'service_active': 'active',
        'out_apis':out_apis,
        'services': services,
        'channels':channels,
        'service_categorys':service_categorys,
        'service_response':service_response,
        'out_micro_services':out_micro_services,
        'service_data':service_data,'view':True
    }

    return render(request, 'Master/service_edit.html', context)

@custom_login_required
def service_delete(request,service_id):
    service = call_delete_method(BASE_URL, f'service-update/{service_id}/', access_token=request.session.get('Token'))
    
    if service.status_code == 200:
        messages.success(request, 'Successfully delete service data', extra_tags='success')
    else:
        messages.error(request, 'Failed to delete service data', extra_tags='warning')
    return redirect('service')


@custom_login_required
def api_parameter(request):
    form = APIParameterForm() 
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []
        
    if request.method == 'POST':
        endpoint = 'api-parameter/'
        form = APIParameterForm(request.POST) 
        if form.is_valid():
            Output = form.cleaned_data
            json_data=json.dumps(Output)
            response=call_post_method(BASE_URL,endpoint,json_data,access_token=request.session.get('Token'))
            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                return redirect('api_parameter')
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
    
    context={
         'form': form,
        'api_parameters_active':'active',
        'api_parameters':api_parameters,
    }
   
    return render(request,'Master/api_parameter.html',context)

@custom_login_required
def api_parameter_edit(request, parameter_id):
    api_parameter_records_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_records_response.status_code == 200:
        api_parameter_records = api_parameter_records_response.json()
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


@custom_login_required
def api_parameter_view(request, parameter_id):
    api_parameter_records_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_records_response.status_code == 200:
        api_parameter_records = api_parameter_records_response.json()
    else:
        api_parameter_records = []

    api_parameter = call_get_method(BASE_URL, f'api-parameter-update/{parameter_id}/', access_token=request.session.get('Token'))
    
    if api_parameter.status_code == 200:
        api_parameter_data = api_parameter.json()
    else:
        messages.error(request, 'Failed to retrieve api_parameter data', extra_tags='warning')
        return redirect('api_parameter')  

    form = APIParameterForm(initial=api_parameter_data)

    context = {
        'form': form,
        'api_parameters_active': 'active',
        'api_parameters': api_parameter_data,
        'api_parameter_records':api_parameter_records,'view':True
    }

    return render(request, 'Master/api_parameter_edit.html', context)

@custom_login_required
def api_parameter_delete(request,api_parameter_id):
    api_parameter = call_delete_method(BASE_URL, f'api-parameter-update/{api_parameter_id}/', access_token=request.session.get('Token'))
    
    if api_parameter.status_code == 200:
        messages.success(request, 'Successfully delete api parameter data', extra_tags='warning')
    else:
        messages.error(request, 'Failed to delete api parameter data', extra_tags='warning')
    return redirect('api_parameter')



@custom_login_required
def serviceplan(request):
    form = ServicePlanForm()
    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []

    serviceplan_response = call_get_method(BASE_URL, 'service-plan/', access_token=request.session.get('Token'))
    if serviceplan_response.status_code == 200:
        serviceplans = serviceplan_response.json()
    else:
        serviceplans = []
        
    if request.method == 'POST':
        endpoint = 'service-plan/'
        form = ServicePlanForm(request.POST) 
        if form.is_valid():
            service_list=request.POST.getlist('service')
            if not isinstance(service_list,list):
                service_list=[service_list]
            json_dataa={
                "service_plan_name":form.cleaned_data['service_plan_name'],
                "description":form.cleaned_data['description'],
                "service":service_list
            }
            json_data = json.dumps(json_dataa)
            response = call_post_method(BASE_URL, endpoint, json_data, access_token=request.session.get('Token'))

            if response.status_code != 200: 
                messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
            else:
                messages.success(request,'Data Saved Successfully',extra_tags='success')
                button = request.POST.get('output_consolidated_btn')
                SP_id = response.json().get('service_plan_id')  # getting service plan id from reponse
                if button:
                    return HttpResponseRedirect(f'/SP_output_consolidation/{SP_id}')
                else:
                    return redirect('serviceplan')
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
    
    context={
         'form': form,
        'serviceplans_active':'active',
        'services':services,
        'serviceplans':serviceplans,
    }
    return render(request,'Master/serviceplan.html',context)

@custom_login_required
def serviceplan_edit(request, serivce_plan_id):
    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []

    serviceplan_records_response = call_get_method(BASE_URL, 'service-plan/', access_token=request.session.get('Token'))
    if serviceplan_records_response.status_code == 200:
        serviceplan_records = serviceplan_records_response.json()
    else:
        serviceplan_records = []
    serviceplan = call_get_method(BASE_URL, f'service-plan-update/{serivce_plan_id}/', access_token=request.session.get('Token'))
    
    if serviceplan.status_code == 200:
        serviceplan_data = serviceplan.json()
    else:
        messages.error(request, 'Failed to retrieve serviceplan data', extra_tags='warning')
        return redirect('serviceplan')  

    if request.method == 'POST':
        form = ServicePlanForm(request.POST, initial=serviceplan_data) 
        if form.is_valid():
            service_list=request.POST.getlist('service')
            if not isinstance(service_list,list):
                service_list=[service_list]
            json_dataa={
                "service_plan_name":form.cleaned_data['service_plan_name'],
                "description":form.cleaned_data['description'],
                "service":service_list
            }
            json_data = json.dumps(json_dataa)
            response = call_put_method(BASE_URL, f'service-plan-update/{serivce_plan_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('serviceplan') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
    else:
        form = ServicePlanForm(initial=serviceplan_data)

    context = {
        'form': form,
        'services':services,
        'serviceplans_active': 'active',
        'serviceplans': serviceplan_data,
        'serviceplan_records':serviceplan_records,
    }

    return render(request, 'Master/serviceplan_edit.html', context)

@custom_login_required
def serviceplan_view(request, serivce_plan_id):
    service_response = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
    if service_response.status_code == 200:
        services = service_response.json()
    else:
        services = []

    serviceplan_records_response = call_get_method(BASE_URL, 'service-plan/', access_token=request.session.get('Token'))
    if serviceplan_records_response.status_code == 200:
        serviceplan_records = serviceplan_records_response.json()
    else:
        serviceplan_records = []
    serviceplan = call_get_method(BASE_URL, f'service-plan-update/{serivce_plan_id}/', access_token=request.session.get('Token'))
    
    if serviceplan.status_code == 200:
        serviceplan_data = serviceplan.json()
    else:
        messages.error(request, 'Failed to retrieve serviceplan data', extra_tags='warning')
        return redirect('serviceplan')  

    form = ServicePlanForm(initial=serviceplan_data)

    context = {
        'form': form,
        'services':services,
        'serviceplans_active': 'active','view':True,
        'serviceplans': serviceplan_data,
        'serviceplan_records':serviceplan_records,
    }

    return render(request, 'Master/serviceplan_edit.html', context)

@custom_login_required
def serviceplan_delete(request,serviceplan_id):
    serviceplan = call_delete_method(BASE_URL, f'service-plan-update/{serviceplan_id}/', access_token=request.session.get('Token'))
    
    if serviceplan.status_code == 200:
        messages.success(request, 'Successfully delete serviceplan data', extra_tags='success')
    else:
        print('serviceplan',serviceplan)
        messages.error(request, 'Failed to delete serviceplan data', extra_tags='warning')
    return redirect('serviceplan')


@custom_login_required
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
                
            
            output_parameter_list=request.POST.getlist('output_parameter')
            if not isinstance(output_parameter_list,list):
                output_parameter_list=[output_parameter_list]
            
            argument=request.POST.getlist('argument')
            if not isinstance(argument,list):
                argument=[argument]

            json_dataa={
                "API_name":form.cleaned_data['API_name'],
                "Http_verbs":form.cleaned_data['Http_verbs'],
                "base_url":form.cleaned_data['base_url'],
                "end_point":form.cleaned_data['end_point'],
                "parameter":parameter_list,
                "out_parameter":output_parameter_list,
                "argument":argument,
                "end_slash":form.cleaned_data['end_slash'],
                "full_url":form.cleaned_data['full_url'],
                "is_auth":form.cleaned_data['is_auth'],
                "description":form.cleaned_data['description'],
            }
            json_data = json.dumps(json_dataa)
            response = call_post_method(BASE_URL, endpoint, json_data, access_token=request.session.get('Token'))
            if response.status_code != 200:
                messages.error(request, f"Oops..! {response.json()}", extra_tags='warning')
            else:
                messages.success(request, 'Data Saved Successfully', extra_tags='success')
                return redirect('api_registration')
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
    
    context={
        'form': form,
        'api_registrations_active':'active',
        'api_registrations':api_registrations,
        'api_parameters':api_parameters,
    }
   
    return render(request,'Master/api_registration.html',context)

@custom_login_required
def api_registration_edit(request, API_id):
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []

    api_registration_records_response = call_get_method(BASE_URL, 'api-register/', access_token=request.session.get('Token'))
    if api_registration_records_response.status_code == 200:
        api_registration_records = api_registration_records_response.json()
    else:
        api_registration_records = []
    api_registration = call_get_method(BASE_URL, f'api-register-update/{API_id}/', access_token=request.session.get('Token'))
    
    if api_registration.status_code == 200:
        api_registration_data = api_registration.json()
    else:
        messages.error(request, 'Failed to retrieve api_registration data', extra_tags='warning')
        return redirect('api_registration')  

    print('api_registration_data',api_registration_data)
    if request.method == 'POST':
        form = ApiRegisterForm(request.POST, initial=api_registration_data) 
        if form.is_valid():
            parameter_list=request.POST.getlist('parameter')
            parameter_list=request.POST.getlist('parameter')
            if not isinstance(parameter_list,list):
                parameter_list=[parameter_list]
                
            
            output_parameter_list=request.POST.getlist('output_parameter')
            if not isinstance(output_parameter_list,list):
                output_parameter_list=[output_parameter_list]
            
            argument=request.POST.getlist('argument')
            if not isinstance(argument,list):
                argument=[argument]

            json_dataa={
                "API_name":form.cleaned_data['API_name'],
                "Http_verbs":form.cleaned_data['Http_verbs'],
                "base_url":form.cleaned_data['base_url'],
                "end_point":form.cleaned_data['end_point'],
                "parameter":parameter_list,
                "out_parameter":output_parameter_list,
                "argument":argument,
                "end_slash":form.cleaned_data['end_slash'],
                "full_url":form.cleaned_data['full_url'],
                "is_auth":form.cleaned_data['is_auth'],
                "description":form.cleaned_data['description'],
            }
            print('json_dataa',json_dataa)
            json_data = json.dumps(json_dataa)
            response = call_put_method(BASE_URL, f'api-register-update/{API_id}/', json_data, access_token=request.session.get('Token'))
            

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('api_registration') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            print(form.errors)
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


@custom_login_required
def api_registration_view(request, API_id):
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []

    api_registration_records_response = call_get_method(BASE_URL, 'api-register/', access_token=request.session.get('Token'))
    if api_registration_records_response.status_code == 200:
        api_registration_records = api_registration_records_response.json()
    else:
        api_registration_records = []
    api_registration = call_get_method(BASE_URL, f'api-register-update/{API_id}/', access_token=request.session.get('Token'))
    
    if api_registration.status_code == 200:
        api_registration_data = api_registration.json()
    else:
        messages.error(request, 'Failed to retrieve api_registration data', extra_tags='warning')
        return redirect('api_registration')  

    form = ApiRegisterForm(initial=api_registration_data)
        

    context = {
        'form': form,
        'api_parameters':api_parameters,
        'api_registrations_active': 'active',
        'api_registrations': api_registration_data,
        'api_registration_records':api_registration_records,'view':True
    }

    return render(request, 'Master/api_registration_edit.html', context)


@custom_login_required
def api_registration_delete(request,api_registration_id):
    api_registration = call_delete_method(BASE_URL, f'api-register-update/{api_registration_id}/', access_token=request.session.get('Token'))
    
    if api_registration.status_code == 200:
        messages.success(request, 'Successfully delete api register data', extra_tags='success')
    else:
        messages.error(request, 'Failed to delete api register data', extra_tags='warning')
    return redirect('api_registration')


@custom_login_required
def process_data_submission(request):
    service_plan_response = call_get_method(BASE_URL, 'service-plan/', access_token=request.session.get('Token'))
    if service_plan_response.status_code == 200:
        service_plans = service_plan_response.json()
    else:
        service_plans = []

    process_response = call_get_method(BASE_URL, 'process/', access_token=request.session.get('Token'))
    if process_response.status_code == 200:
        processs = process_response.json()
    else:
        processs = []
        
    if request.method == 'POST':
        form = ProcessDataForm(request.POST)
        if form.is_valid():
            depending_service_plan_list = request.POST.getlist('depending_service_plan')
            service_plan_list = request.POST.getlist('service_plan')
            is_depending_list = request.POST.getlist('is_depending')
            processserviceplan_set = []
            # Iterate over the lists and create dictionaries for each item
            for service_plan, is_depending, depending_service_plan in zip(service_plan_list, is_depending_list, depending_service_plan_list):

                item = {
                    "service_plan": service_plan,
                    "is_depending": is_depending,
                    "depending_service_plan": depending_service_plan,
                }

                processserviceplan_set.append(item)


            # Convert the form data to a JSON structure
            data = {
                "process_name": form.cleaned_data['process_name'],
                "description": form.cleaned_data['description'],
                "processserviceplan_set": processserviceplan_set
            }
            depending_service_plan=request.POST.getlist('depending_service_plan')
            endpoint = 'process/'
            response=call_post_method(BASE_URL,endpoint,json.dumps(data),access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('process')
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
                messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
    else:
        form = ProcessDataForm()
    
    context={
        'form': form,
        'processs_active':'active',
        'processs':processs,
        'service_plans':service_plans
    }

    return render(request, 'Master/process.html', context)


@custom_login_required
def process_edit(request,process_id):
    service_plan_response = call_get_method(BASE_URL, 'service-plan/', access_token=request.session.get('Token'))
    if service_plan_response.status_code == 200:
        service_plans = service_plan_response.json()
    else:
        service_plans = []

    process_response = call_get_method(BASE_URL, 'process/', access_token=request.session.get('Token'))
    if process_response.status_code == 200:
        processs = process_response.json()
    else:
        processs = []

    process_record_response = call_get_method(BASE_URL, f'process-update/{process_id}/', access_token=request.session.get('Token'))
    if process_record_response.status_code == 200:
        processs_record = process_record_response.json()
    else:
        messages.error(request, 'Failed to retrieve process data', extra_tags='warning')
        return redirect('process')
        
    if request.method == 'POST':
        form = ProcessDataForm(request.POST, initial=processs_record)
        if form.is_valid():
            depending_service_plan_list = request.POST.getlist('depending_service_plan')
            pre_depending_service_plan_list = request.POST.getlist('pre_depending_service_plan')
            pre_service_plan_list = request.POST.getlist('pre_service_plan')
            service_plan_list = request.POST.getlist('service_plan')
            pre_is_depending_list = request.POST.getlist('pre_is_depending')
            is_depending_list = request.POST.getlist('is_depending')
            processserviceplan_set = []
            depending_SP_list = pre_depending_service_plan_list + depending_service_plan_list
            SP_list = pre_service_plan_list + service_plan_list
            depending_list = pre_is_depending_list + is_depending_list
            
            # Iterate over the lists and create dictionaries for each item
            for service_plan, is_depending, depending_service_plan in zip(SP_list, depending_list, depending_SP_list):
                if service_plan != '':
                    item = {
                        "service_plan": service_plan,
                        "is_depending": is_depending,
                        "depending_service_plan": depending_service_plan,
                    }

                    processserviceplan_set.append(item)


            # Convert the form data to a JSON structure
            data = {
                "process_name": form.cleaned_data['process_name'],
                "description": form.cleaned_data['description'],
                "processserviceplan_set": processserviceplan_set
            }
            depending_service_plan=request.POST.getlist('depending_service_plan')
            endpoint = f'process-update/{process_id}/'
            response=call_put_method(BASE_URL,endpoint,json.dumps(data),access_token=request.session.get('Token'))
            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('process')
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
                messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
    else:
        form = ProcessDataForm(initial=processs_record)
    print('processs_record',processs_record)
    context={
        'form': form,
        'processs_active':'active',
        'processs':processs,
        'service_plans':service_plans,'processs_record':processs_record,
    }

    return render(request, 'Master/process_edit.html', context)

@custom_login_required
def process_view(request,process_id):
    service_plan_response = call_get_method(BASE_URL, 'service-plan/', access_token=request.session.get('Token'))
    if service_plan_response.status_code == 200:
        service_plans = service_plan_response.json()
    else:
        service_plans = []

    process_response = call_get_method(BASE_URL, 'process/', access_token=request.session.get('Token'))
    if process_response.status_code == 200:
        processs = process_response.json()
    else:
        processs = []

    process_record_response = call_get_method(BASE_URL, f'process-update/{process_id}/', access_token=request.session.get('Token'))
    if process_record_response.status_code == 200:
        processs_record = process_record_response.json()
    else:
        messages.error(request, 'Failed to retrieve process data', extra_tags='warning')
        return redirect('process')
        
    form = ProcessDataForm(initial=processs_record)
    print('processs_record',processs_record)
    context={
        'form': form,
        'processs_active':'active',
        'processs':processs,
        'service_plans':service_plans,'processs_record':processs_record,'view':True
    }

    return render(request, 'Master/process_edit.html', context)

@custom_login_required
def process_delete(request,process_id):
    process = call_delete_method(BASE_URL, f'process-update/{process_id}/', access_token=request.session.get('Token'))
    
    if process.status_code == 200:
        messages.success(request, 'Successfully delete api register data', extra_tags='success')
    else:
        messages.error(request, 'Failed to delete api register data', extra_tags='warning')
    return redirect('process')


@custom_login_required
def service_orchestration(request):
    process_response = call_get_method(BASE_URL, 'process/', access_token=request.session.get('Token'))
    if process_response.status_code == 200:
        process_records = process_response.json()
    else:
        process_records = []
    service_orchestration_response = call_get_method(BASE_URL, 'service-orchestration/', access_token=request.session.get('Token'))
    if service_orchestration_response.status_code == 200:
        service_orchestration = service_orchestration_response.json()
    else:
        service_orchestration = []

    if request.method == 'POST':
        form = ServiceOrchestrationForm(request.POST)
        if form.is_valid():
            depending_process_list = request.POST.getlist('depending_process')
            process_list = request.POST.getlist('process')
            is_depending_list = request.POST.getlist('is_depending')
            service_orchestration_set = []
            # Iterate over the lists and create dictionaries for each item
            for process, is_depending, depending_process in zip(process_list, is_depending_list, depending_process_list):

                item = {
                    "process": process,
                    "is_depending": is_depending,
                    "depending_process": depending_process,
                }
                service_orchestration_set.append(item)


            # Convert the form data to a JSON structure
            data = {
                "service_orchestration_name": form.cleaned_data['orchestration_name'],
                "description": form.cleaned_data['description'],
                "service_orchestration_set": service_orchestration_set
            }
            depending_process=request.POST.getlist('depending_process')
            endpoint = 'service-orchestration/'
            response=call_post_method(BASE_URL,endpoint,json.dumps(data),access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('service_orchestration')
            else:
                error_message = response
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
    else:
        form = ServiceOrchestrationForm()
    
    context={
        'form': form,
        'service_orchestration_active':'active',
        'service_orchestration':service_orchestration,
        'process':process_records
    }

    return render(request, 'Master/service_orchestration.html', context)


@custom_login_required
def service_orchestration_edit(request,SO_id):
    process_response = call_get_method(BASE_URL, 'process/', access_token=request.session.get('Token'))
    if process_response.status_code == 200:
        process_records = process_response.json()
    else:
        process_records = []
    service_orchestration_response = call_get_method(BASE_URL, 'service-orchestration/', access_token=request.session.get('Token'))
    if service_orchestration_response.status_code == 200:
        service_orchestration = service_orchestration_response.json()
    else:
        service_orchestration = []

        
    SO_record_response = call_get_method(BASE_URL, f'service-orchestration-update/{SO_id}/', access_token=request.session.get('Token'))
    if SO_record_response.status_code == 200:
        SO_record = SO_record_response.json()
        SO_record['orchestration_name']=SO_record['service_orchestration_name']
    else:
        messages.error(request, 'Failed to retrieve process data', extra_tags='warning')
        return redirect('process')
    service_orchestration_process_response = call_get_method(BASE_URL, f'service-orchestration-process/{SO_id}/', access_token=request.session.get('Token'))
    if service_orchestration_process_response.status_code == 200:
        service_orchestration_process = service_orchestration_process_response.json()
    else:
        service_orchestration_process = []


    if request.method == 'POST':
        form = ServiceOrchestrationForm(request.POST,initial=SO_record)
        if form.is_valid():
            new_depending_process_list = request.POST.getlist('depending_process')
            new_process_list = request.POST.getlist('process')
            new_is_depending_list = request.POST.getlist('is_depending')
            
            pre_depending_process_list = request.POST.getlist('pre_depending_process')
            pre_process_list = request.POST.getlist('pre_process')
            pre_is_depending_list = request.POST.getlist('pre_is_depending')
            depending_process_list = pre_depending_process_list + new_depending_process_list
            process_list= pre_process_list + new_process_list
            is_depending_list= pre_is_depending_list + new_is_depending_list
            service_orchestration_set = []
            # Iterate over the lists and create dictionaries for each item
            for process, is_depending, depending_process in zip(process_list, is_depending_list, depending_process_list):
                if process != '':
                    item = {
                        "process": process,
                        "is_depending": is_depending,
                        "depending_process": depending_process,
                    }
                    service_orchestration_set.append(item)


            # Convert the form data to a JSON structure
            data = {
                "service_orchestration_name": form.cleaned_data['orchestration_name'],
                "description": form.cleaned_data['description'],
                "service_orchestration_set": service_orchestration_set
            }
            endpoint = f'service-orchestration-update/{SO_id}/'
            response=call_put_method(BASE_URL,endpoint,json.dumps(data),access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('service_orchestration')
            else:
                error_message = response
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
    else:
        form = ServiceOrchestrationForm(initial=SO_record)
    
    context={
        'form': form,
        'service_orchestration_active':'active',
        'service_orchestration':service_orchestration,
        'process':process_records,'service_orchestration_process':service_orchestration_process
    }

    return render(request, 'Master/service_orchestration_edit.html', context)

@custom_login_required
def service_orchestration_delete(request,SO_id):
    process = call_delete_method(BASE_URL, f'service-orchestration-update/{SO_id}/', access_token=request.session.get('Token'))
    
    if process.status_code == 200:
        messages.success(request, 'Successfully delete api SO', extra_tags='success')
    else:
        messages.error(request, 'Failed to delete SO data', extra_tags='warning')
    return redirect('service_orchestration')



@custom_login_required
def service_orchestration_view(request,SO_id):
    process_response = call_get_method(BASE_URL, 'process/', access_token=request.session.get('Token'))
    if process_response.status_code == 200:
        process_records = process_response.json()
    else:
        process_records = []
    service_orchestration_response = call_get_method(BASE_URL, 'service-orchestration/', access_token=request.session.get('Token'))
    if service_orchestration_response.status_code == 200:
        service_orchestration = service_orchestration_response.json()
    else:
        service_orchestration = []

        
    SO_record_response = call_get_method(BASE_URL, f'service-orchestration-update/{SO_id}/', access_token=request.session.get('Token'))
    if SO_record_response.status_code == 200:
        SO_record = SO_record_response.json()
        SO_record['orchestration_name']=SO_record['service_orchestration_name']
    else:
        messages.error(request, 'Failed to retrieve process data', extra_tags='warning')
        return redirect('process')
    service_orchestration_process_response = call_get_method(BASE_URL, f'service-orchestration-process/{SO_id}/', access_token=request.session.get('Token'))
    if service_orchestration_process_response.status_code == 200:
        service_orchestration_process = service_orchestration_process_response.json()
    else:
        service_orchestration_process = []


    form = ServiceOrchestrationForm(initial=SO_record)
    
    context={
        'form': form,
        'service_orchestration_active':'active',
        'service_orchestration':service_orchestration,'view':True,
        'process':process_records,'service_orchestration_process':service_orchestration_process,
    }

    return render(request, 'Master/service_orchestration_edit.html', context)


@custom_login_required
def output_consolidation(request):
    form = OutputConsolidationForm()
    if request.method == 'POST':
        form = OutputConsolidationForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            SOID = form.cleaned_data['service_orchestration_id']
            PID = form.cleaned_data['process_id']
            SPID = form.cleaned_data['service_plan_id']
            if SOID:
                output_consolidation_level = 'SO'
                output_consolidation_level_id = SOID
            elif PID:
                output_consolidation_level ="P"
                output_consolidation_level_id = PID
            elif SPID:
                output_consolidation_level ="SP"
                output_consolidation_level_id = SPID
            else:
                messages.error(request, f"Fill any one id", extra_tags='warning')
                return redirect('output_consolidation')
            
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
            return redirect('output_consolidation')
        endpoint = 'get-output-consolidation/'
        response=call_post_method(BASE_URL,endpoint,json.dumps(form_data),access_token=request.session.get('Token'))

        if response.status_code == 200:
            messages.success(request, 'Data fetch Successfully', extra_tags='success')
            process_records = response.json()
        else:
            error_message = response.json()
            messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            return redirect('output_consolidation')

       
        context={
            'output_consolidation_active':'active','process_records':process_records,'form':form,'output_consolidation_level':output_consolidation_level,
            'output_consolidation_level_id':output_consolidation_level_id,
        }
        return render(request,'Master/SP_output_consolidation.html',context)
    
    context={
        'serviceplans_active':'active','form':form
    }
    return render(request,'Master/SP_output_consolidation.html',context)


@custom_login_required
def output_consolidation_save(request):
    request_data = []
    api_id_list = request.POST.getlist('api_id')
    for api_id in api_id_list:
        dict={}
        dict['api'] = api_id
        dict['output_consolidation_level'] =  request.POST.get('output_consolidation_level')
        dict['output_consolidation_level_id'] = request.POST.get('output_consolidation_level_id')
        dict['out_parameter'] = request.POST.getlist(api_id,[])
        if len(dict['out_parameter']) > 0:
            request_data.append(dict)


    endpoint='output-consolidation/'
    json_data = json.dumps(request_data)
    response = call_post_method(BASE_URL, endpoint, json_data, access_token=request.session.get('Token'))
    if response.status_code != 200:
        messages.error(request,f"Oops..! {response.json()}",extra_tags='warning')
        return redirect('output_consolidation')
    else:
        messages.success(request,'Data Saved Successfully',extra_tags='success')
        return redirect('output_consolidation')

@custom_login_required
def micro_service_registration(request):
    form = MicroServiceRegisterForm()
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []


    api_registration_response = call_get_method(BASE_URL, 'micro-service-registration/', access_token=request.session.get('Token'))
    if api_registration_response.status_code == 200:
        api_registrations = api_registration_response.json()
    else:
        api_registrations = []
        

    if request.method == 'POST':
        endpoint = 'micro-service-registration/'
        form = MicroServiceRegisterForm(request.POST) 
        if form.is_valid():
            parameter_list=request.POST.getlist('parameter')
            if not isinstance(parameter_list,list):
                parameter_list=[parameter_list]
            
            output_parameter_list=request.POST.getlist('output_parameter')
            if not isinstance(output_parameter_list,list):
                output_parameter_list=[output_parameter_list]
            json_dataa={
                "m_service_id":form.cleaned_data['micro_service_id'],
                "base_url":form.cleaned_data['base_url'],
                "end_point":form.cleaned_data['end_point'],
                "parameter":parameter_list,
                "out_parameter":output_parameter_list,
                "full_url":form.cleaned_data['full_url'],
                "is_auth":form.cleaned_data['is_authenticated'],
                "retry_count":form.cleaned_data['retry_count'],
                "description":form.cleaned_data['description'],
            }
            json_data = json.dumps(json_dataa)
            response = call_post_method(BASE_URL, endpoint, json_data, access_token=request.session.get('Token'))
            if response.status_code != 200:
                messages.error(request, f"Oops..! {response.json()}", extra_tags='warning')
            else:
                messages.success(request, 'Data Saved Successfully', extra_tags='success')
                return redirect('micro_service_registration')
        else:
            messages.error(request, f"Oops..! {form.errors}", extra_tags='warning')
    
    context={
        'form': form,
        'ms_registrations_active':'active',
        'api_registrations':api_registrations,
        'api_parameters':api_parameters,
    }

    return render(request, 'Master/micro_service_registration.html', context)



@custom_login_required
def micro_service_registration_edit(request, micro_service_id):
    
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []


    api_registration_response = call_get_method(BASE_URL, 'micro-service-registration/', access_token=request.session.get('Token'))
    if api_registration_response.status_code == 200:
        api_registrations = api_registration_response.json()
    else:
        api_registrations = []

    micro_service_response  = call_get_method(BASE_URL, f'micro-service-update/{micro_service_id}/', access_token=request.session.get('Token'))
    
    if micro_service_response.status_code == 200:
        micro_service_data = micro_service_response.json()
    else:
        print(micro_service_response)
        messages.error(request, 'Failed to retrieve micro_service data', extra_tags='warning')
        return redirect('micro_service_registration')  
    form = MicroServiceRegisterForm(initial=micro_service_data)
    if request.method == 'POST':
        endpoint=f'micro-service-update/{micro_service_id}/'
        form = MicroServiceRegisterForm(request.POST, initial=micro_service_data) 
        if form.is_valid():
            parameter_list=request.POST.getlist('parameter')
            if not isinstance(parameter_list,list):
                parameter_list=[parameter_list]
            
            output_parameter_list=request.POST.getlist('output_parameter')
            if not isinstance(output_parameter_list,list):
                output_parameter_list=[output_parameter_list]
            json_dataa={
                "m_service_id":form.cleaned_data['micro_service_id'],
                "base_url":form.cleaned_data['base_url'],
                "end_point":form.cleaned_data['end_point'],
                "parameter":parameter_list,
                "out_parameter":output_parameter_list,
                "full_url":form.cleaned_data['full_url'],
                "is_auth":form.cleaned_data['is_authenticated'],
                "retry_count":form.cleaned_data['retry_count'],
                "description":form.cleaned_data['description'],
            }
            json_data = json.dumps(json_dataa)
            response = call_put_method(BASE_URL, endpoint, json_data, access_token=request.session.get('Token'))
            if response.status_code != 200:
                messages.error(request, f"Oops..! {response.json()}", extra_tags='warning')
            else:
                messages.success(request, 'Data Saved Successfully', extra_tags='success')
                return redirect('micro_service_registration')
            response = call_put_method(BASE_URL, f'micro-service-update/{micro_service_id}/', json_data, access_token=request.session.get('Token'))

            if response.status_code == 200:
                messages.success(request, 'Data Updated Successfully', extra_tags='success')
                return redirect('micro_service_registration') 
            else:
                error_message = response.json()
                messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.', extra_tags='warning')
   

    context = {
        'form': form,
        'ms_registrations_active':'active',
        'api_registrations':api_registrations,
        'api_parameters':api_parameters,'micro_service_data':micro_service_data
    }

    return render(request, 'Master/micro_service_registration_edit.html', context)


@custom_login_required
def micro_service_registration_view(request, micro_service_id):
    
    api_parameter_response = call_get_method(BASE_URL, 'api-parameter/', access_token=request.session.get('Token'))
    if api_parameter_response.status_code == 200:
        api_parameters = api_parameter_response.json()
    else:
        api_parameters = []


    api_registration_response = call_get_method(BASE_URL, 'micro-service-registration/', access_token=request.session.get('Token'))
    if api_registration_response.status_code == 200:
        api_registrations = api_registration_response.json()
    else:
        api_registrations = []

    micro_service_response  = call_get_method(BASE_URL, f'micro-service-update/{micro_service_id}/', access_token=request.session.get('Token'))
    
    if micro_service_response.status_code == 200:
        micro_service_data = micro_service_response.json()
    else:
        print(micro_service_response)
        messages.error(request, 'Failed to retrieve micro_service data', extra_tags='warning')
        return redirect('micro_service_registration')  
    form = MicroServiceRegisterForm(initial=micro_service_data)

    context = {
        'form': form,
        'ms_registrations_active':'active',
        'api_registrations':api_registrations,
        'api_parameters':api_parameters,'micro_service_data':micro_service_data,'view':True
    }

    return render(request, 'Master/micro_service_registration_edit.html', context)

@custom_login_required
def micro_service_registration_delete(request,micro_service_id):
    micro_service_registration = call_delete_method(BASE_URL, f'micro-service-update/{micro_service_id}/', access_token=request.session.get('Token'))
    
    if micro_service_registration.status_code == 200:
        messages.success(request, 'Successfully delete api parameter data', extra_tags='success')
    else:
        messages.error(request, 'Failed to delete api parameter data', extra_tags='warning')
    return redirect('micro_service_registration')


@custom_login_required
def bulk_delete(request):
    channels = record_get('channel/',request.session.get('Token'))
    if request.method == 'POST':
        delete_btn = request.POST.get('delete')
        if delete_btn == 'delete':
            service_id = request.POST.getlist('service_ids')
            print('service_id',service_id)
            json_data = {'service_ids':service_id}
            response = call_post_method(BASE_URL, 'Bulk-delete-MicroService/', json.dumps(json_data), access_token=request.session.get('Token'))
            print('response',response)
            print('response',response.json())
            return redirect ('bulk_delete')
        else:
            channel_id = request.POST.get('channel')
            print('channel_id',channel_id)
            service_records = call_get_method(BASE_URL, 'service/', access_token=request.session.get('Token'))
            print(service_records)
            filtered_list=[]
            for obj in service_records.json():
                # print('obj',obj)
                if obj['channel'] == channel_id:
                    filtered_list.append(obj)
            # print('api_registration_response',filtered_list)
            context={
                'bulk_delete_active':'active',
                'channels':channels,
                'filtered_list':filtered_list
            }
            return render(request, 'Master/bulk_delete.html', context)
    context={
        'bulk_delete_active':'active',
        'channels':channels,
    }
    return render(request, 'Master/bulk_delete.html', context)