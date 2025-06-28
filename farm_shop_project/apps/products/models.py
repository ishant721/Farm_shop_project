# farm_shop_project/apps/products/models.py
from django.db import models
from apps.users.models import CustomUser
from django.db.models import Q
import uuid
from django.utils import timezone # <--- Ensure timezone is imported for default


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Selling price
    stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default="piece", help_text="e.g., kg, dozen, piece, bag")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, help_text="Upload a product image")
    
    is_approved = models.BooleanField(default=False, help_text="Whether this product has been approved by an admin to be publicly listed.")
    
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_products', help_text="User who created this product.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']
        permissions = [
            ("can_add_unapproved_product", "Can add product (unapproved by default)"),
            ("can_approve_product", "Can approve product for listing"),
            ("can_manage_stock", "Can manage product stock (purchases, sales)"),
            ("can_generate_receipts", "Can generate sales receipts"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'pk': self.pk})


class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        ordering = ['name']

    def __str__(self):
        return self.name

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost per unit bought from supplier")
    # --- START OF CHANGE ---
    # Changed from auto_now_add=True to default=timezone.localdate
    purchase_date = models.DateField(default=timezone.localdate)
    # --- END OF CHANGE ---
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_purchases')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"
        ordering = ['-purchase_date', '-created_at']

    def __str__(self):
        return f"Purchase of {self.quantity} {self.product.unit} of {self.product.name} from {self.supplier.name if self.supplier else 'N/A'}"

    @property
    def total_cost(self):
        return self.quantity * self.unit_cost

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    customer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_sales', limit_choices_to={'user_type__in': ['farmer', 'business', 'employee']})
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price per unit")
    # --- START OF CHANGE ---
    # Changed from auto_now_add=True to default=timezone.localdate
    sale_date = models.DateField(default=timezone.localdate)
    # --- END OF CHANGE ---
    
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="GST rate in percentage (e.g., 5, 12, 18)")
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    receipt_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_sales_by')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"
        ordering = ['-sale_date', '-created_at']

    def __str__(self):
        return f"Sale #{self.pk} of {self.quantity} {self.product.unit} of {self.product.name} for ${self.grand_total}"

    @property
    def total_revenue(self):
        return self.quantity * self.unit_price

    def calculate_totals(self):
        self.sub_total = self.total_revenue
        self.gst_amount = (self.sub_total * self.gst_rate) / 100
        self.grand_total = self.sub_total + self.gst_amount

    def save(self, *args, **kwargs):
        self.calculate_totals()
        if not self.receipt_number:
            self.receipt_number = f"SALE-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def get_receipt_url(self):
        from django.urls import reverse
        return reverse('products:sale_receipt_detail', kwargs={'receipt_number': self.receipt_number})