from functools import wraps
from django.shortcuts import redirect

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the session variable exists
        if 'Token' not in request.session:
            return redirect('SignIn')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
