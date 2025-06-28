# apps/businesses/urls.py
from django.urls import path
from .views import BusinessDashboardView

app_name = 'businesses'

urlpatterns = [
    path('dashboard/', BusinessDashboardView.as_view(), name='dashboard'),
    # Add more business-specific URLs here (e.g., /b2b/bulk-orders, /b2b/invoices)
]