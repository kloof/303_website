from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_logs_page, name='admin_logs_page'),
    path('api/', views.AdminLogListAPI.as_view(), name='admin_logs_api'),
]
