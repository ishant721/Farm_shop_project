# farm_shop_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.users.urls')),
    path('', include('apps.core.urls')),
    path('dashboard/', include('apps.dashboards.urls')),

    path('employee/', include('apps.employees.urls')),
    path('farmer/', include('apps.farmers.urls')),
    path('b2b/', include('apps.businesses.urls')),

    path('products/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
    path('finance/', include('apps.finance.urls')), # <--- NEW APP URL
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)