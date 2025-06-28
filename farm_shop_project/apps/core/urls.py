# farm_shop_project/apps/core/urls.py
from django.urls import path
from .views import HomePageView, AboutUsView, ContactUsView, ServicesView # <--- UPDATED IMPORT

app_name = 'core'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    # --- START OF NEW ADDITION ---
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('services/', ServicesView.as_view(), name='services'),
    # --- END OF NEW ADDITION ---
]