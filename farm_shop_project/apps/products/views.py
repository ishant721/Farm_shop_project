# farm_shop_project/apps/products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.db import models # Needed for models.F
from django.utils import timezone
from datetime import datetime # Needed for datetime.strptime in PaymentReminderView (if moved here, currently in finance app)

from .models import Product, Supplier, Purchase, Sale
from .forms import ProductForm, SupplierForm, PurchaseForm, SaleForm
from apps.users.utils import (
    send_new_product_awaiting_approval_email,
    send_product_approval_status_email,
    send_purchase_notification_email,
    send_sale_notification_email,
    send_sale_receipt_email # For sending sales receipts via email
)

# --- Public Facing Views ---
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_approved=True)
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_approved=True)
        return queryset

# --- Admin/Employee Product/Stock/Sales Management Views ---

# Mixin for Admin or Employee access
class AdminEmployeeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or \
               self.request.user.user_type in ['admin', 'employee']

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this management area.")
        return redirect('dashboards:dashboard_redirect')

# Mixin for Admin only access
class AdminOnlyRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to perform this action.")
        return redirect('dashboards:dashboard_redirect')

# --- Product Management ---
class ProductManagementListView(AdminEmployeeRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_management_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.user_type == 'employee' and not self.request.user.is_superuser:
             messages.info(self.request, "As an employee, you see products awaiting review. Only Admins can approve products.")
             queryset = queryset.filter(is_approved=False)
        return queryset.order_by('-created_at')

class ProductCreateView(AdminEmployeeRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_management_list')

    def form_valid(self, form):
        form.instance.is_approved = False
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        send_new_product_awaiting_approval_email(form.instance)
        messages.success(self.request, "Product added successfully! It is awaiting admin approval to be listed publicly.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Add New Product"
        return context

class ProductUpdateView(AdminOnlyRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_management_list')

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Edit Product"
        return context

class ProductDeleteView(AdminOnlyRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_management_list')
    context_object_name = 'product'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        product_name = self.object.name
        self.object.delete()
        messages.success(request, f"Product '{product_name}' deleted successfully! Stock adjusted.")
        return redirect(self.get_success_url())

class ProductToggleApprovalView(AdminOnlyRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        product.is_approved = not product.is_approved
        product.save()
        status_message = "approved" if product.is_approved else "unapproved"
        messages.success(request, f"Product '{product.name}' has been {status_message}.")
        send_product_approval_status_email(product)
        return redirect(reverse_lazy('products:product_management_list'))

# --- Supplier Management Views ---
class SupplierListView(AdminOnlyRequiredMixin, ListView):
    model = Supplier
    template_name = 'products/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10
    ordering = ['name']

class SupplierCreateView(AdminOnlyRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'products/supplier_form.html'
    success_url = reverse_lazy('products:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Add New Supplier"
        return context

class SupplierUpdateView(AdminOnlyRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'products/supplier_form.html'
    success_url = reverse_lazy('products:supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Edit Supplier"
        return context

class SupplierDeleteView(AdminOnlyRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'products/supplier_confirm_delete.html'
    success_url = reverse_lazy('products:supplier_list')
    context_object_name = 'supplier'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        supplier_name = self.object.name
        self.object.delete()
        messages.success(request, f"Supplier '{supplier_name}' deleted successfully!")
        return redirect(self.get_success_url())

# --- Purchase Management Views ---
class PurchaseListView(AdminEmployeeRequiredMixin, ListView):
    model = Purchase
    template_name = 'products/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 10
    ordering = ['-purchase_date', '-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.user_type == 'employee' and not user.is_superuser:
            queryset = queryset.filter(created_by=user)
            messages.info(self.request, "As an employee, you only see purchases you have recorded.")
        return queryset

class PurchaseCreateView(AdminEmployeeRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'products/purchase_form.html'
    success_url = reverse_lazy('products:purchase_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        product = form.instance.product
        product.stock += form.instance.quantity
        product.save()

        send_purchase_notification_email(form.instance)

        messages.success(self.request, f"Purchase of {form.instance.quantity} {product.unit} of {product.name} recorded successfully! Stock updated.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Record New Purchase"
        return context

class PurchaseDetailView(AdminEmployeeRequiredMixin, DetailView):
    model = Purchase
    template_name = 'products/purchase_detail.html'
    context_object_name = 'purchase'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.user_type == 'employee' and not user.is_superuser:
            queryset = queryset.filter(created_by=user)
        return queryset

class PurchaseDeleteView(AdminOnlyRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'products/purchase_confirm_delete.html'
    success_url = reverse_lazy('products:purchase_list')
    context_object_name = 'purchase'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        product = self.object.product
        quantity = self.object.quantity
        purchase_id = self.object.pk
        
        product.stock -= quantity
        product.save()

        self.object.delete()
        messages.success(request, f"Purchase record #{purchase_id} deleted successfully! Stock adjusted.")
        return redirect(self.get_success_url())

# --- Sale Management Views ---
class SaleListView(AdminEmployeeRequiredMixin, ListView):
    model = Sale
    template_name = 'products/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 10
    ordering = ['-sale_date', '-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.user_type == 'employee' and not user.is_superuser:
            queryset = queryset.filter(created_by=user)
            messages.info(self.request, "As an employee, you only see sales you have recorded.")
        return queryset

class SaleCreateView(AdminEmployeeRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'products/sale_form.html'
    def get_success_url(self):
        # Redirect to the receipt detail view after successful sale creation
        return reverse_lazy('products:sale_receipt_detail', kwargs={'receipt_number': self.object.receipt_number})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        
        response = super().form_valid(form) # Save Sale (stock validation and total calculations happen in model's save)
        
        # Update Product Stock (deduct)
        product = form.instance.product
        product.stock -= form.instance.quantity
        product.save()

        send_sale_notification_email(form.instance)
        # Send receipt email to customer (if email exists)
        if form.instance.customer and form.instance.customer.email:
            send_sale_receipt_email(form.instance, request=self.request)

        messages.success(self.request, f"Sale of {form.instance.quantity} {product.unit} of {product.name} recorded successfully! Stock updated. Receipt generated.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Record New Sale"
        return context

class SaleDetailView(AdminEmployeeRequiredMixin, DetailView):
    model = Sale
    template_name = 'products/sale_detail.html'
    context_object_name = 'sale'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.user_type == 'employee' and not user.is_superuser:
            queryset = queryset.filter(created_by=user)
        return queryset

class SaleDeleteView(AdminOnlyRequiredMixin, DeleteView):
    model = Sale
    template_name = 'products/sale_confirm_delete.html'
    success_url = reverse_lazy('products:sale_list')
    context_object_name = 'sale'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        product = self.object.product
        quantity = self.object.quantity
        sale_id = self.object.pk
        
        product.stock += quantity
        product.save()

        self.object.delete()
        messages.success(request, f"Sale record #{sale_id} deleted successfully! Stock adjusted.")
        return redirect(self.get_success_url())

# --- Receipt Views ---

class ReceiptDetailView(AdminEmployeeRequiredMixin, DetailView):
    model = Sale
    template_name = 'products/sale_receipt_detail.html'
    context_object_name = 'sale'
    slug_field = 'receipt_number'
    slug_url_kwarg = 'receipt_number'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add company details for the receipt if needed, can be from settings
        # context['company_name'] = "Farm Shop"
        # context['company_address'] = "123 Farm Fresh Lane, Rural Town, State 12345"
        # context['company_contact'] = "info@farmshop.com | +1 234 567 890"
        return context

class ReceiptPrintView(AdminEmployeeRequiredMixin, DetailView):
    model = Sale
    template_name = 'products/sale_receipt_print.html'
    context_object_name = 'sale'
    slug_field = 'receipt_number'
    slug_url_kwarg = 'receipt_number'

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = "Farm Shop"
        context['company_address'] = "123 Farm Fresh Lane, Rural Town, State 12345"
        context['company_contact'] = "info@farmshop.com | +1 234 567 890"
        context['receipt_date'] = timezone.localdate()
        return context

# --- Send Receipt Email View ---
class SendReceiptEmailView(AdminEmployeeRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        sale = get_object_or_404(Sale, pk=pk)
        
        if not sale.customer or not sale.customer.email:
            messages.error(request, f"Customer for Sale #{sale.pk} does not have an email address to send receipt.")
            return redirect(reverse_lazy('products:sale_receipt_detail', kwargs={'receipt_number': sale.receipt_number}))
        
        email_sent = send_sale_receipt_email(sale, request=request)

        if email_sent:
            messages.success(request, f"Receipt for Sale #{sale.pk} sent to {sale.customer.email}.")
        else:
            messages.error(request, f"Failed to send receipt for Sale #{sale.pk}. Check email settings or customer email.")
        
        return redirect(reverse_lazy('products:sale_receipt_detail', kwargs={'receipt_number': sale.receipt_number}))