from django import forms
from mainapp.api_call import call_get_method,call_post_method,call_post_method_for_without_token, call_put_method
import requests

BASE_URL = 'http://127.0.0.1:5565/api/'

class SignInForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ChannelForm(forms.Form):
    channel_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
  
class ServiceCategoryMasterForm(forms.Form):
    service_category_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
  
class ServiceForm(forms.Form):   
    service_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    service_category = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    channel = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    out_API=forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
  
class APIParameterForm(forms.Form):
    parameter_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_requried = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class': 'form-control'}))

class ProcessForm(forms.Form):
    process_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    service_plan = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
class ServicePlanForm(forms.Form):   
    service_plan_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

class ApiRegisterForm(forms.Form):
    API_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    HTTP_VERBS = (
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("DELETE", "DELETE"),
        ("PATCH", "PATCH"),
    )
    
    Http_verbs = forms.ChoiceField(choices=HTTP_VERBS, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    base_url = forms.URLField(required=True, widget=forms.URLInput(attrs={'class': 'form-control'}))
    end_point = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # parameter = forms.MultipleChoiceField(
    #     widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    #     required=False
    # )


# class processForm(forms.Form):
#     service_plan = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    