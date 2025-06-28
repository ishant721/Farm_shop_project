# farm_shop_project/apps/finance/models.py
from django.db import models
from apps.users.models import CustomUser
from django.utils import timezone # <--- Added for timezone.localdate()
from django.db.models import F # Added for F expressions in queries (e.g., amount_due)


class FarmerBill(models.Model):
    farmer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bills', limit_choices_to={'user_type': 'farmer'})
    
    # Bill details
    description = models.TextField(blank=True, help_text="Optional description for the bill (e.g., 'Produce purchase for May')")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Payment due date - entered by admin/employee
    due_date = models.DateField()

    # Approval Status - Employee requests, Admin approves
    is_approved = models.BooleanField(default=False, help_text="True if the bill has been approved by an admin.")
    
    # Who created the bill (employee or admin)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='bills_created')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Farmer Bill"
        verbose_name_plural = "Farmer Bills"
        ordering = ['-created_at']
        permissions = [
            ("can_create_farmer_bill", "Can create a farmer bill (requires admin approval)"),
            ("can_approve_farmer_bill", "Can approve a farmer bill"),
            ("can_send_payment_reminders", "Can send payment reminders to farmers"),
            ("can_view_all_bills", "Can view all farmer bills (not just own/pending)")
        ]

    def __str__(self):
        return f"Bill #{self.pk} for {self.farmer.username} - ${self.total_amount}"

    @property
    def amount_due(self):
        return self.total_amount - self.paid_amount

    @property
    def payment_status(self):
        if self.amount_due <= 0:
            return 'Paid'
        elif self.due_date < timezone.localdate():
            return 'Overdue'
        elif self.paid_amount > 0 and self.amount_due > 0:
            return 'Partially Paid'
        else:
            return 'Due'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('finance:bill_detail', kwargs={'pk': self.pk})