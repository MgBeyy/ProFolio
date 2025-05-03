from os import environ
environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')

import django
django.setup



def get_current_host_url(request):
    """
    Gets protocol and host information from the given request object and returns the full URL.
    """
    protocol = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    return f"{protocol}://{host}/"

