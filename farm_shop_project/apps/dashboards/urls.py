# apps/dashboards/urls.py
from django.urls import path
from .views import DashboardRedirectView

app_name = 'dashboards'

urlpatterns = [
    path('', DashboardRedirectView.as_view(), name='dashboard_redirect'),
]