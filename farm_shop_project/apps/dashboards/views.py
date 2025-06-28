# apps/dashboards/views.py
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages

class DashboardRedirectView(LoginRequiredMixin, View):
    """
    Redirects authenticated users to their specific dashboard based on their user_type.
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        # --- START OF CHANGE ---
        if user.is_superuser or user.user_type == 'admin':
            return redirect(reverse_lazy('users:admin_dashboard')) # Redirect to new custom admin dashboard
        # --- END OF CHANGE ---
        elif user.user_type == 'employee':
            return redirect(reverse_lazy('employees:dashboard'))
        elif user.user_type == 'farmer' or user.user_type == 'farmer_employee':
            return redirect(reverse_lazy('farmers:dashboard'))
        elif user.user_type == 'business':
            return redirect(reverse_lazy('businesses:dashboard'))
        else:
            messages.warning(request, "Your user type does not have an associated dashboard yet.")
            return redirect(reverse_lazy('users:profile'))