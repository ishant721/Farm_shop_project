# apps/employees/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect # <--- ADD THIS IMPORT!


class EmployeeDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'employees/dashboard.html'

    def test_func(self):
        return self.request.user.user_type == 'employee' or self.request.user.is_superuser

    def handle_no_permission(self):
        # The 'redirect' function was not imported, causing the NameError.
        # It needs to be imported from django.shortcuts.
        return redirect('dashboards:dashboard_redirect') # Redirect to general dashboard redirect