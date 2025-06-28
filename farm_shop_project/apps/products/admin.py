# farm_shop_project/apps/products/admin.py
from django.contrib import admin
from .models import Product, Supplier, Purchase, Sale

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'unit', 'is_approved', 'created_at', 'creator')
    list_filter = ('is_approved', 'unit', 'created_at', 'creator')
    search_fields = ('name', 'description')
    actions = ['make_approved', 'make_unapproved']

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {'fields': ('name', 'description', 'price', 'stock', 'unit', 'image')}),
        )
        if request.user.is_superuser or request.user.is_staff:
            fieldsets += (
                ('Approval Status', {'fields': ('is_approved',), 'classes': ('collapse',)}),
                ('Audit Info', {'fields': ('creator',), 'classes': ('collapse',)})
            )
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser and not request.user.is_staff:
            if 'is_approved' in form.base_fields:
                del form.base_fields['is_approved']
            if 'creator' in form.base_fields:
                del form.base_fields['creator']
            if 'stock' in form.base_fields:
                form.base_fields['stock'].widget.attrs['readonly'] = 'readonly'
                form.base_fields['stock'].help_text = "Stock is updated automatically by purchases and sales."
        return form

    def make_approved(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} products successfully marked as approved.", level='success')
    make_approved.short_description = "Mark selected products as approved"

    def make_unapproved(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} products successfully marked as unapproved.", level='warning')
    make_unapproved.short_description = "Mark selected products as unapproved"

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_approved and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone_number', 'email', 'created_at')
    search_fields = ('name', 'contact_person', 'phone_number', 'email')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'supplier', 'quantity', 'unit_cost', 'total_cost', 'purchase_date', 'created_by')
    list_filter = ('purchase_date', 'supplier', 'created_by', 'product')
    search_fields = ('product__name', 'supplier__name', 'created_by__username', 'pk')
    raw_id_fields = ('product', 'supplier', 'created_by')
    date_hierarchy = 'purchase_date'

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'customer', 'quantity', 'unit_price', 'sub_total', 'gst_rate', 'gst_amount', 'grand_total', 'sale_date', 'receipt_number', 'created_by') # <--- UPDATED list_display
    list_filter = ('sale_date', 'customer', 'created_by', 'product')
    search_fields = ('product__name', 'customer__username', 'created_by__username', 'receipt_number', 'pk') # <--- UPDATED search_fields
    raw_id_fields = ('product', 'customer', 'created_by')
    date_hierarchy = 'sale_date'
    
    # --- START OF NEW ADDITION ---
    readonly_fields = ('gst_amount', 'sub_total', 'grand_total', 'receipt_number') # These are calculated or auto-generated
    
    fieldsets = (
        (None, {'fields': ('product', 'customer', 'quantity', 'unit_price', 'sale_date')}),
        ('GST & Totals', {'fields': ('gst_rate', ('sub_total', 'gst_amount', 'grand_total')), 'classes': ('collapse',)}),
        ('Receipt & Audit', {'fields': ('receipt_number', 'created_by', 'created_at'), 'classes': ('collapse',)})
    )
    # --- END OF NEW ADDITION ---

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        # The calculate_totals() and receipt_number generation happen in the model's save method
        super().save_model(request, obj, form, change)