# apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from django.urls import reverse # No longer needed for custom admin URL
# from django.utils.html import format_html # No longer needed
from .models import CustomUser, OneTimePassword

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'phone_number')}),
    )
    list_display = UserAdmin.list_display + ('user_type', 'phone_number', 'is_active')
    list_filter = UserAdmin.list_filter + ('user_type', 'is_active')
    search_fields = ('username', 'email', 'phone_number')

    # --- START OF CHANGE ---
    # Removed custom URL and button injection for add_employee_view,
    # as this is now handled by the custom admin dashboard.
    # def get_urls(self):
    #     urls = super().get_urls()
    #     from django.urls import path
    #     custom_urls = [
    #         path('add_employee/', self.admin_site.admin_view(self.add_employee_view), name='add_employee'),
    #     ]
    #     return custom_urls + urls

    # def add_employee_view(self, request):
    #     return redirect(reverse('users:admin_create_employee'))

    # def changelist_view(self, request, extra_context=None):
    #     extra_context = extra_context or {}
    #     extra_context['show_add_employee_button'] = True
    #     return super().changelist_view(request, extra_context=extra_context)

    # def employee_actions(self, obj):
    #     if obj.user_type == 'employee' and not obj.is_active:
    #         return format_html('<a class="button" href="#">Resend Credentials</a> ')
    #     return ""
    # employee_actions.short_description = "Employee Actions"
    # employee_actions.allow_tags = True
    # --- END OF CHANGE ---

@admin.register(OneTimePassword)
class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'otp', 'created_at', 'expires_at', 'is_used', 'is_valid')
    list_filter = ('is_used', 'otp', 'expires_at')
    search_fields = ('user__username', 'user__email', 'email', 'otp')
    readonly_fields = ('created_at', 'expires_at', 'is_used')