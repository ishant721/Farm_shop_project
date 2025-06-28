# apps/employees/urls.py
from django.urls import path
from .views import EmployeeDashboardView

app_name = 'employees'

urlpatterns = [
    path('dashboard/', EmployeeDashboardView.as_view(), name='dashboard'),
    # Add more employee-specific URLs here (e.g., /employee/orders, /employee/inventory)
]