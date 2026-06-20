from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
import json

def index(request):

    return render(request, 'index.html')

def admin_panel(request):
    return render(request, 'admin_panel.html')
