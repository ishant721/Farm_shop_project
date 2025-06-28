# farm_shop_project/apps/finance/admin.py
from django.contrib import admin
from .models import FarmerBill
# from django.db.models import F # Not directly used in admin.py itself now, but good practice to keep if used elsewhere

@admin.register(FarmerBill)
class FarmerBillAdmin(admin.ModelAdmin):
    list_display = ('pk', 'farmer', 'total_amount', 'paid_amount', 'amount_due', 'due_date', 'payment_status', 'is_approved', 'created_by', 'created_at')
    list_filter = (
        'is_approved',
        'due_date',
        'created_at',
        'farmer',
        'created_by',
        # Removed non-existent filters like GreaterThanFilter or custom property filters
    )
    search_fields = ('farmer__username', 'farmer__email', 'description', 'pk')
    raw_id_fields = ('farmer', 'created_by') # Use raw_id_fields for FKs to CustomUser for better UX with many users
    date_hierarchy = 'created_at' # Provides date-based navigation in admin
    
    # Custom actions
    actions = ['mark_approved', 'mark_rejected', 'mark_paid']

    # Read-only fields for staff
    def get_readonly_fields(self, request, obj=None):
        if obj: # Editing an existing object
            # Once approved, some fields might become read-only to prevent tampering
            # Only superusers can modify approved status or total/paid amount of approved bills
            if obj.is_approved and not request.user.is_superuser:
                return ('farmer', 'total_amount', 'paid_amount', 'due_date', 'created_by', 'is_approved', 'created_at', 'updated_at')
            # For non-approved, employee can edit most fields
            return ('created_by', 'created_at', 'updated_at')
        return ('created_by', 'created_at', 'updated_at') # For new object creation (fields like created_by, created_at)

    # Fieldsets for better organization in admin change form
    fieldsets = (
        (None, {
            'fields': ('farmer', 'description', ('total_amount', 'paid_amount'), 'due_date'),
        }),
        ('Approval & Tracking', {
            'fields': ('is_approved', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',), # Makes this section collapsible in admin
        }),
    )

    # get_fieldsets is usually for dynamic fieldset display based on user/object,
    # if `is_approved` visibility needs to be controlled beyond read_only_fields.
    # The current `get_readonly_fields` covers most needs for this.
    def get_fieldsets(self, request, obj=None):
        # This just calls super, so it uses the fieldsets defined above
        return super().get_fieldsets(request, obj)

    def mark_approved(self, request, queryset):
        # Only admins/superusers can approve
        if not request.user.is_superuser and request.user.user_type != 'admin':
            self.message_user(request, "You do not have permission to approve bills.", level='error')
            return
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} bills successfully marked as approved.", level='success')
        # Here you might send notification emails (though utils.py functions are designed for views)
    mark_approved.short_description = "Mark selected bills as approved"

    def mark_rejected(self, request, queryset):
        # Only admins/superusers can reject
        if not request.user.is_superuser and request.user.user_type != 'admin':
            self.message_user(request, "You do not have permission to reject bills.", level='error')
            return
        updated = queryset.update(is_approved=False) # For rejection, set is_approved to False
        self.message_user(request, f"{updated} bills successfully marked as rejected (unapproved).", level='warning')
    mark_rejected.short_description = "Mark selected bills as rejected"

    def mark_paid(self, request, queryset):
        # Only admins/superusers/employees can mark as paid (depending on workflow)
        if not request.user.is_superuser and request.user.user_type not in ['admin', 'employee']:
            self.message_user(request, "You do not have permission to mark bills as paid.", level='error')
            return
        for bill in queryset:
            bill.paid_amount = bill.total_amount # Mark as fully paid
            bill.save()
        self.message_user(request, f"{queryset.count()} bills successfully marked as fully paid.", level='success')
    mark_paid.short_description = "Mark selected bills as fully paid"