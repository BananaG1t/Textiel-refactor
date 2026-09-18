from django.http import HttpResponse
from django.template import loader

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render(request=request))

def settings(request):
    template = loader.get_template('settings.html')
    return HttpResponse(template.render(request=request))