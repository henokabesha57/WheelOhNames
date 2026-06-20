from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='wheel_index'),
    path('admin-panel/', views.admin_panel, name='wheel_admin_panel'),
]