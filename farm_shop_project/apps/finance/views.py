# farm_shop_project/apps/finance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.db import models
from django.utils import timezone
from datetime import datetime # Needed for datetime.strptime

from .models import FarmerBill
from .forms import FarmerBillForm
from apps.users.models import CustomUser
from apps.users.utils import send_bill_awaiting_approval_email, send_bill_status_update_email, send_payment_reminder_email

# --- Mixins for Access Control ---
class FinanceAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for views that require access to finance operations.
    Superuser, Admin, Employee roles.
    """
    def test_func(self):
        return self.request.user.is_superuser or \
               self.request.user.user_type in ['admin', 'employee']

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access finance operations.")
        return redirect('dashboards:dashboard_redirect')

class AdminOnlyFinanceMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin for views that require Admin-only access for finance operations.
    Superuser, Admin roles.
    """
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to perform this finance action.")
        return redirect('dashboards:dashboard_redirect')

# --- Farmer Bill Management Views ---

class FarmerBillListView(FinanceAccessMixin, ListView):
    model = FarmerBill
    template_name = 'finance/farmer_bill_list.html'
    context_object_name = 'bills'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser or user.user_type == 'admin':
            # Admins/Superusers see all bills
            pass
        elif user.user_type == 'employee':
            # Employees see bills they created and unapproved bills
            queryset = queryset.filter(Q(created_by=user) | Q(is_approved=False)) # Employees see their own or pending bills
            messages.info(self.request, "As an employee, you see bills you've created or bills awaiting approval.")
        elif user.user_type == 'farmer':
            # Farmers only see their own bills
            queryset = queryset.filter(farmer=user, is_approved=True) # Farmers only see approved bills
            messages.info(self.request, "As a farmer, you see your approved bills.")
            
        # Optional filtering by status, search query
        status_filter = self.request.GET.get('status')
        if status_filter:
            if status_filter == 'overdue':
                queryset = queryset.filter(due_date__lt=timezone.localdate(), paid_amount__lt=models.F('total_amount'))
            elif status_filter == 'paid':
                queryset = queryset.filter(paid_amount__gte=models.F('total_amount'))
            elif status_filter == 'pending_approval':
                queryset = queryset.filter(is_approved=False)
            elif status_filter == 'approved':
                queryset = queryset.filter(is_approved=True, paid_amount__lt=models.F('total_amount'))
            
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(farmer__username__icontains=search_query) |
                Q(farmer__first_name__icontains=search_query) |
                Q(farmer__last_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filtering options to context for the template
        context['status_options'] = ['all', 'overdue', 'paid', 'pending_approval', 'approved']
        context['current_status_filter'] = self.request.GET.get('status', 'all')
        context['search_query'] = self.request.GET.get('q', '')
        context['today'] = timezone.localdate() # Pass today's date for template comparisons

        # Add a flag to each bill object indicating if the "Remind to Pay" button should be shown
        user = self.request.user
        for bill in context['bills']:
            bill.can_send_reminder = (
                bill.amount_due > 0 and 
                bill.is_approved and 
                (user.is_superuser or user.user_type == 'admin' or user.user_type == 'employee')
            )
        return context


class FarmerBillCreateView(FinanceAccessMixin, CreateView):
    model = FarmerBill
    form_class = FarmerBillForm
    template_name = 'finance/farmer_bill_form.html'
    success_url = reverse_lazy('finance:bill_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user # Set the employee/admin who created the bill
        form.instance.is_approved = False # All bills require approval first
        
        response = super().form_valid(form) # Save the bill

        # Send email to admin about new bill awaiting approval
        send_bill_awaiting_approval_email(form.instance)

        messages.success(self.request, f"Bill for {form.instance.farmer.username} added successfully! It is awaiting admin approval.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Create New Farmer Bill"
        return context

class FarmerBillDetailView(FinanceAccessMixin, DetailView):
    model = FarmerBill
    template_name = 'finance/farmer_bill_detail.html'
    context_object_name = 'bill'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_superuser and user.user_type not in ['admin', 'employee']:
            # Farmers can only see their own approved bills
            queryset = queryset.filter(farmer=user, is_approved=True)
        elif user.user_type == 'employee' and not user.is_superuser:
            # Employees can see their own created bills, or pending bills
            queryset = queryset.filter(Q(created_by=user) | Q(is_approved=False))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.localdate()

        # Add a flag to the bill object indicating if the "Remind to Pay" button should be shown
        user = self.request.user
        bill = context['bill'] # Get the bill object from context
        bill.can_send_reminder = (
            bill.amount_due > 0 and 
            bill.is_approved and 
            (user.is_superuser or user.user_type == 'admin' or user.user_type == 'employee')
        )
        return context

class FarmerBillUpdateView(AdminOnlyFinanceMixin, UpdateView): # Only Admins can update bills
    model = FarmerBill
    form_class = FarmerBillForm
    template_name = 'finance/farmer_bill_form.html'
    success_url = reverse_lazy('finance:bill_list')

    def form_valid(self, form):
        messages.success(self.request, f"Bill #{form.instance.pk} updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = "Edit Farmer Bill"
        return context

class FarmerBillDeleteView(AdminOnlyFinanceMixin, DeleteView): # Only Admins can delete bills
    model = FarmerBill
    template_name = 'finance/farmer_bill_confirm_delete.html'
    success_url = reverse_lazy('finance:bill_list')
    context_object_name = 'bill'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        bill_id = self.object.pk
        bill_farmer_name = self.object.farmer.username
        self.object.delete()
        messages.success(request, f"Bill #{bill_id} for {bill_farmer_name} deleted successfully!")
        return redirect(self.get_success_url())

class FarmerBillApproveRejectView(AdminOnlyFinanceMixin, View):
    """
    Handles approval/rejection of a farmer bill.
    """
    def post(self, request, pk, *args, **kwargs):
        bill = get_object_or_404(FarmerBill, pk=pk)
        action = request.POST.get('action') # 'approve' or 'reject'

        if action == 'approve':
            bill.is_approved = True
            bill.save()
            messages.success(request, f"Bill #{bill.pk} for {bill.farmer.username} approved successfully!")
            send_bill_status_update_email(bill) # Notify creator and farmer
        elif action == 'reject':
            bill.is_approved = False # Keep as unapproved
            bill.save() # Mark as unapproved in case it was approved by mistake
            messages.warning(request, f"Bill #{bill.pk} for {bill.farmer.username} marked as rejected (unapproved).")
            send_bill_status_update_email(bill) # Notify creator and farmer
        else:
            messages.error(request, "Invalid action for bill approval.")
        
        return redirect(reverse_lazy('finance:bill_list'))


class PaymentReminderView(FinanceAccessMixin, View):
    """
    Sends a payment reminder email to the farmer for a specific bill.
    Can also update due date if provided in POST.
    """
    def post(self, request, pk, *args, **kwargs):
        bill = get_object_or_404(FarmerBill, pk=pk)
        
        # Get the new_due_date_str from POST data. It will be an empty string if nothing is selected.
        # .strip() is crucial to handle whitespace.
        new_due_date_str = request.POST.get('new_due_date', '').strip()

        effective_due_date = bill.due_date
        
        # Check if new_due_date_str has a non-empty value BEFORE attempting to parse.
        # This handles empty strings ('') after stripping.
        if new_due_date_str: 
            try:
                # Attempt to parse the string. datetime.strptime handles 'YYYY-MM-DD'.
                new_due_date = timezone.localdate(datetime.strptime(new_due_date_str, '%Y-%m-%d'))
                
                # Only update if the new date is actually different from the current bill due date
                if new_due_date != bill.due_date:
                    bill.due_date = new_due_date
                    bill.save()
                    effective_due_date = new_due_date
                    messages.info(request, f"Bill #{bill.pk} due date updated to {effective_due_date.strftime('%Y-%m-%d')}.")
            except ValueError:
                # This block catches if the string is *not* in 'YYYY-MM-DD' format (e.g., if someone typed garbage)
                messages.error(request, "Invalid date format provided for new due date. Please use YYYY-MM-DD.")
                return redirect(reverse_lazy('finance:bill_list'))
        # If new_due_date_str is empty after stripping, or was never provided, it falls through
        # and uses the bill's original effective_due_date.

        send_payment_reminder_email(bill, effective_due_date)
        messages.success(request, f"Payment reminder sent to {bill.farmer.username} for Bill #{bill.pk}.")
        
        return redirect(reverse_lazy('finance:bill_list'))