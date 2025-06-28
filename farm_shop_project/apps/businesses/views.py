# apps/businesses/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class BusinessDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'businesses/dashboard.html'

    def test_func(self):
        return self.request.user.user_type == 'business' or self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('dashboard_redirect')