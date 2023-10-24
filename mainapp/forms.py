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
  