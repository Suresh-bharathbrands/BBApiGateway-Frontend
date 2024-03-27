from os import access
import requests

def call_post_method_for_without_token(BASE_URL,endpoint,data):
    api_url=BASE_URL+endpoint
    headers = {
        'Content-Type': 'application/json',
        
    }
    response = requests.post(api_url,data=data,headers=headers)
    return response

def call_post_method(BASE_URL,endpoint,data, access_token):
    api_url=BASE_URL+endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(api_url,data=data,headers=headers)
    return response


def call_get_method(BASE_URL, endpoint, access_token):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        return response
    
    
    
def call_put_method(BASE_URL, endpoint, data, access_token):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.put(api_url, data=data, headers=headers)
    if response.status_code == 200:
        return response
    else:
        return response
    
def call_delete_method(BASE_URL, endpoint, access_token):
    api_url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.delete(api_url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        return response
    