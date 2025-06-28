# apps/farmers/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class FarmerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'farmers/dashboard.html'

    def test_func(self):
        # Farmers and Farmer Employees can access this dashboard
        return self.request.user.user_type in ['farmer', 'farmer_employee'] or self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('dashboard_redirect')