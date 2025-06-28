# farm_shop_project/apps/finance/urls.py
from django.urls import path
from .views import (
    FarmerBillListView,
    FarmerBillCreateView,
    FarmerBillDetailView,
    FarmerBillUpdateView,
    FarmerBillDeleteView,
    FarmerBillApproveRejectView,
    PaymentReminderView
)

app_name = 'finance'

urlpatterns = [
    path('bills/', FarmerBillListView.as_view(), name='bill_list'),
    path('bills/create/', FarmerBillCreateView.as_view(), name='bill_create'),
    path('bills/<int:pk>/', FarmerBillDetailView.as_view(), name='bill_detail'),
    path('bills/<int:pk>/edit/', FarmerBillUpdateView.as_view(), name='bill_edit'),
    path('bills/<int:pk>/delete/', FarmerBillDeleteView.as_view(), name='bill_delete'),
    path('bills/<int:pk>/approve-reject/', FarmerBillApproveRejectView.as_view(), name='bill_approve_reject'),
    path('bills/<int:pk>/send-reminder/', PaymentReminderView.as_view(), name='send_payment_reminder'),
]