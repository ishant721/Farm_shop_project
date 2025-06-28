# farm_shop_project/apps/core/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from apps.products.models import Product

class HomePageView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_approved=True, stock__gt=0).order_by('-created_at')[:4]
        return context

# --- START OF NEW ADDITION ---
class AboutUsView(TemplateView):
    template_name = 'core/about_us.html'

class ContactUsView(TemplateView):
    template_name = 'core/contact_us.html'

class ServicesView(TemplateView):
    template_name = 'core/services.html'
# --- END OF NEW ADDITION ---