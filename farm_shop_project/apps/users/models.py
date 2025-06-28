# farm_shop_project/apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db.models import Q

import random
import string

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('admin', 'Admin'),
        ('employee', 'Farm Shop Employee'),
        ('farmer', 'Farmer'),
        ('business', 'Business Client'),
        ('farmer_employee', 'Farmer Employee'),
    )
    user_type = models.CharField(max_length=20, choices=USER_ROLES, default='farmer')
    phone_number = PhoneNumberField(blank=True, null=True, unique=True, help_text="Enter phone number with country code (e.g., +12125552368)")
    email = models.EmailField(unique=True, blank=False, null=False)

    date_of_birth = models.DateField(null=True, blank=True)

    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    is_active = models.BooleanField(
        ('active'),
        default=False,
        help_text=(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.user_type})"

    @staticmethod
    def make_random_password(length=12):
        """Generates a random password for users created by admin."""
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for i in range(length))

    # --- START OF CHANGE ---
    def save(self, *args, **kwargs):
        # If the user is a superuser, ensure their user_type is 'admin'
        if self.is_superuser and self.user_type != 'admin':
            self.user_type = 'admin'
        elif not self.is_superuser and self.user_type == 'admin' and self.pk:
            # If an existing admin user is somehow demoted from superuser,
            # but their user_type is still 'admin', you might want to force a change
            # to prevent a 'regular' user from having 'admin' type.
            # However, usually, user_type='admin' is reserved for superusers.
            # If you want specific 'admin' non-superuser accounts, then this 'elif' is tricky.
            # For our current setup, 'admin' user_type implicitly means superuser.
            # If you allow non-superuser 'admin' users, this check needs more nuance.
            # For simplicity, we assume 'admin' type is tied to 'is_superuser'.
            # If a superuser is set to false, they should lose their 'admin' user_type too.
            # For now, let's just make sure superusers *are* admin.
            pass # Keep it simple for now: superuser status overrides user_type to 'admin'

        super().save(*args, **kwargs)
    # --- END OF CHANGE ---

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        permissions = [
            ("can_access_employee_dashboard", "Can access employee dashboard"),
            ("can_access_farmer_dashboard", "Can access farmer dashboard"),
            ("can_access_business_dashboard", "Can access business dashboard"),
        ]

class OneTimePassword(models.Model):
    OTP_TYPES = (
        ('registration', 'Registration Verification'),
        ('password_reset', 'Password Reset Verification'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=False)
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES, default='registration')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"OTP for {self.user.email if self.user else self.email} ({self.otp_type}) - {self.otp}"

    class Meta:
        verbose_name = "One Time Password"
        verbose_name_plural = "One Time Passwords"
        constraints = [
            models.CheckConstraint(
                check=Q(user__isnull=False) | Q(email__isnull=False),
                name='user_or_email_must_be_present'
            )
        ]