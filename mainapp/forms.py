from django import forms


class SignInForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ChannelForm(forms.Form):
    channel_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
  
class ServiceCategoryMasterForm(forms.Form):
    service_category_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
  