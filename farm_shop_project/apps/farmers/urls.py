# apps/farmers/urls.py
from django.urls import path
from .views import FarmerDashboardView

app_name = 'farmers'

urlpatterns = [
    path('dashboard/', FarmerDashboardView.as_view(), name='dashboard'),
    # Add more farmer-specific URLs here (e.g., /farmer/my-products, /farmer/payouts)
]