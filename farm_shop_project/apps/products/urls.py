# apps/products/urls.py
from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductManagementListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    ProductToggleApprovalView,
    SupplierListView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,
    PurchaseListView, PurchaseCreateView, PurchaseDetailView, PurchaseDeleteView,
    SaleListView, SaleCreateView, SaleDetailView, SaleDeleteView,
    ReceiptDetailView, ReceiptPrintView,
    SendReceiptEmailView # <--- NEW IMPORT
)

app_name = 'products'

urlpatterns = [
    # Public Product Listings
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    # Admin/Employee Product Management
    path('manage/', ProductManagementListView.as_view(), name='product_management_list'),
    path('add/', ProductCreateView.as_view(), name='product_add'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('<int:pk>/toggle-approval/', ProductToggleApprovalView.as_view(), name='product_toggle_approval'),

    # Supplier Management
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),

    # Purchase Management
    path('purchases/', PurchaseListView.as_view(), name='purchase_list'),
    path('purchases/record/', PurchaseCreateView.as_view(), name='purchase_record'),
    path('purchases/<int:pk>/', PurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchases/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='purchase_delete'),

    # Sale Management
    path('sales/', SaleListView.as_view(), name='sale_list'),
    path('sales/record/', SaleCreateView.as_view(), name='sale_record'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale_detail'),
    path('sales/<int:pk>/delete/', SaleDeleteView.as_view(), name='sale_delete'),

    # Receipt URLs
    path('sales/receipt/<str:receipt_number>/', ReceiptDetailView.as_view(), name='sale_receipt_detail'),
    path('sales/receipt/<str:receipt_number>/print/', ReceiptPrintView.as_view(), name='sale_receipt_print'),
    
    # --- START OF NEW ADDITION: URL for sending receipt email ---
    path('sales/<int:pk>/send-receipt-email/', SendReceiptEmailView.as_view(), name='send_receipt_email'),
    # --- END OF NEW ADDITION ---
]