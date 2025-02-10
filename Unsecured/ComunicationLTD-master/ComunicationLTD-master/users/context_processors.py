from django.conf import settings # import the settings file

def should_enable_xss(request):
    return {'ENABLE_XSS': settings.XSS}
