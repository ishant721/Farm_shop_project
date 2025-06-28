# apps/users/utils.py
import random
from datetime import timedelta, date
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse

# from twilio.rest import Client
# from twilio.base.exceptions import TwilioRestException

from .models import OneTimePassword, CustomUser
from apps.products.models import Product, Purchase, Sale
# Assuming apps.finance.models.FarmerBill exists
try:
    from apps.finance.models import FarmerBill
except ImportError:
    class FarmerBill:
        pass


def generate_otp():
    """Generates a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp, username=None, context_data=None, subject_prefix="Farm Shop Verification"):
    """
    Sends an OTP email to the specified recipient using a template.
    """
    if not context_data:
        context_data = {}

    context = {
        'otp': otp,
        'username': username if username else email,
        'otp_validity_minutes': settings.OTP_VALIDITY_MINUTES,
        'site_name': 'Farm Shop',
        **context_data
    }
    html_message = render_to_string('users/otp_email.html', context)
    plain_message = f"Your OTP for Farm Shop is: {otp}. It is valid for {settings.OTP_VALIDITY_MINUTES} minutes."

    subject = f"{subject_prefix}: Your One-Time Password"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        print(f"OTP email sent to {email} successfully.")
        return True
    except Exception as e:
        print(f"Error sending OTP email to {email}: {e}")
        return False

def create_and_send_otp(user_or_email, otp_type='registration', request=None):
    """
    Creates an OTP entry and sends it via email.
    `user_or_email` can be a CustomUser object or an email string.
    """
    otp_code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=settings.OTP_VALIDITY_MINUTES)

    user_obj = None
    email_str = None
    username = None

    if isinstance(user_or_email, CustomUser):
        user_obj = user_or_email
        email_str = user_obj.email
        username = user_obj.username
    elif isinstance(user_or_email, str):
        email_str = user_or_email
        try:
            user_obj = CustomUser.objects.get(email__iexact=email_str)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            username = email_str
    else:
        raise ValueError("user_or_email must be a CustomUser instance or an email string.")

    OneTimePassword.objects.filter(
        (models.Q(user=user_obj) if user_obj else models.Q(email__iexact=email_str)),
        otp_type=otp_type,
        is_used=False,
        expires_at__gt=timezone.now()
    ).update(is_used=True)

    otp_instance = OneTimePassword.objects.create(
        user=user_obj,
        email=email_str,
        otp=otp_code,
        expires_at=expires_at,
        otp_type=otp_type
    )

    context_data = {
        'otp_type': otp_type.replace('_', ' ').title(),
    }
    subject_prefix = f"Farm Shop {otp_type.replace('_', ' ').title()}"

    if send_otp_email(email_str, otp_code, username, context_data, subject_prefix):
        return otp_instance
    else:
        otp_instance.delete()
        return None

def send_password_reset_otp_email(user):
    """
    Sends an OTP for password reset to the user.
    """
    return create_and_send_otp(user, otp_type='password_reset')

def send_employee_credentials_email(employee_user, raw_password, request):
    """
    Sends an email to a newly created employee with their login credentials.
    """
    context = {
        'employee_username': employee_user.username,
        'employee_email': employee_user.email,
        'raw_password': raw_password,
        'login_url': request.build_absolute_uri(reverse('users:login')),
        'site_name': 'Farm Shop',
    }
    html_message = render_to_string('users/employee_welcome_email.html', context)
    plain_message = (
        f"Dear {employee_user.first_name if employee_user.first_name else employee_user.username},\n\n"
        f"Welcome to Farm Shop! Your admin has created an employee account for you.\n\n"
        f"Your login details are:\n"
        f"Username: {employee_user.username}\n"
        f"Password: {raw_password}\n\n"
        f"You can log in here: {request.build_absolute_uri(reverse('users:login'))}\n\n"
        f"Please change your password after your first login for security reasons.\n\n"
        f"Best regards,\nThe Farm Shop Admin Team"
    )

    subject = "Welcome to Farm Shop! Your Employee Account Details"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [employee_user.email]

    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        print(f"Employee welcome email sent to {employee_user.email} successfully.")
        return True
    except Exception as e:
        print(f"Error sending employee welcome email to {employee_user.email}: {e}")
        return False

def send_birthday_wishing_email(user):
    """
    Sends a birthday wishing email to the user.
    """
    context = {
        'user': user,
        'site_name': 'Farm Shop',
        'current_year': date.today().year,
    }
    html_message = render_to_string('users/birthday_email.html', context)
    plain_message = (
        f"Happy Birthday, {user.first_name if user.first_name else user.username}!\n\n"
        f"The entire team at Farm Shop wishes you a very happy birthday!\n"
        f"We hope you have a fantastic day filled with joy and celebration.\n\n"
        f"Best regards,\nThe Farm Shop Team"
    )

    subject = "Happy Birthday from Farm Shop!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        print(f"Birthday email sent to {user.email} successfully.")
        return True
    except Exception as e:
        print(f"Error sending birthday email to {user.email}: {e}")
        return False

def _get_admin_emails():
    """Helper to get a list of active superuser and admin employee emails."""
    admin_users = CustomUser.objects.filter(
        Q(is_superuser=True) | Q(user_type='admin'),
        is_active=True,
        email__isnull=False
    ).values_list('email', flat=True)
    return list(admin_users)

def send_general_notification_email(recipient_list, subject, template_name, context):
    """
    Sends a general notification email using a specified template.
    """
    context.update({'site_name': 'Farm Shop'})
    html_message = render_to_string(template_name, context)
    plain_message = ""
    
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        print(f"General notification email '{subject}' sent to {', '.join(recipient_list)} successfully.")
        return True
    except Exception as e:
        print(f"Error sending general notification email '{subject}' to {', '.join(recipient_list)}: {e}")
        return False

def send_new_farmer_registration_email(farmer_user):
    """Sends an email to admins when a new farmer registers."""
    admin_emails = _get_admin_emails()
    if not admin_emails:
        print("WARNING: No active admin emails found to send new farmer registration notification.")
        return False

    subject = "New Farmer Registered on Farm Shop"
    template = 'users/notification_new_farmer_registration.html'
    context = {
        'farmer_username': farmer_user.username,
        'farmer_email': farmer_user.email,
        'farmer_phone': farmer_user.phone_number,
        'registration_date': farmer_user.date_joined,
    }
    if hasattr(settings, 'BASE_URL'):
        context['admin_dashboard_url'] = settings.BASE_URL + settings.LOGIN_REDIRECT_URL
    else:
        context['admin_dashboard_url'] = 'http://127.0.0.1:8000' + settings.LOGIN_REDIRECT_URL

    return send_general_notification_email(admin_emails, subject, template, context)

def send_new_product_awaiting_approval_email(product):
    """Sends an email to admins when a new product is added (and needs approval)."""
    admin_emails = _get_admin_emails()
    if not admin_emails:
        print("WARNING: No active admin emails found to send new product approval notification.")
        return False

    subject = "New Product Awaiting Approval on Farm Shop"
    template = 'users/notification_new_product_awaiting_approval.html'
    context = {
        'product_name': product.name,
        'product_description': product.description,
        'product_price': product.price,
        'product_creator_username': product.creator.username if product.creator else 'N/A',
    }
    if hasattr(settings, 'BASE_URL'):
        context['product_management_url'] = settings.BASE_URL + reverse('products:product_management_list')
    else:
        context['product_management_url'] = 'http://127.0.0.1:8000' + reverse('products:product_management_list')

    return send_general_notification_email(admin_emails, subject, template, context)

def send_product_approval_status_email(product):
    """Sends an email to the product creator when its approval status changes."""
    if not product.creator or not product.creator.email:
        print(f"WARNING: Cannot send product approval status email for {product.name}: No creator email found.")
        return False

    subject = f"Your Product '{product.name}' Status Update"
    template = 'users/notification_product_approval_status.html'
    context = {
        'product_name': product.name,
        'product_status': 'Approved' if product.is_approved else 'Unapproved',
        'creator_username': product.creator.username,
    }
    if hasattr(settings, 'BASE_URL'):
        context['product_link'] = settings.BASE_URL + product.get_absolute_url()
    else:
        context['product_link'] = 'http://127.0.0.1:8000' + product.get_absolute_url()

    return send_general_notification_email([product.creator.email], subject, template, context)

def send_bill_awaiting_approval_email(bill):
    """Sends an email to admins when a new farmer bill is created and needs approval."""
    admin_emails = _get_admin_emails()
    if not admin_emails:
        print("WARNING: No active admin emails found to send new bill approval notification.")
        return False

    subject = f"New Farmer Bill Awaiting Approval (Bill #{bill.pk})"
    template = 'users/notification_bill_awaiting_approval.html'
    context = {
        'bill_id': bill.pk,
        'farmer_username': bill.farmer.username,
        'total_amount': bill.total_amount,
        'paid_amount': bill.paid_amount,
        'amount_due': bill.amount_due,
        'due_date': bill.due_date,
        'created_by_username': bill.created_by.username if bill.created_by else 'N/A',
    }
    if hasattr(settings, 'BASE_URL'):
        context['bill_management_url'] = settings.BASE_URL + reverse('finance:bill_list')
    else:
        context['bill_management_url'] = 'http://127.0.0.1:8000' + reverse('finance:bill_list')

    return send_general_notification_email(admin_emails, subject, template, context)

def send_bill_status_update_email(bill):
    """Sends an email to the bill creator and farmer when a bill's approval status changes."""
    recipient_emails = []
    if bill.created_by and bill.created_by.email:
        recipient_emails.append(bill.created_by.email)
    if bill.farmer and bill.farmer.email:
        recipient_emails.append(bill.farmer.email)
    
    if not recipient_emails:
        print(f"WARNING: Cannot send bill status update email for Bill #{bill.pk}: No recipient emails found.")
        return False

    subject = f"Your Bill (ID: #{bill.pk}) Status Update"
    template = 'users/notification_bill_status_update.html'
    context = {
        'bill_id': bill.pk,
        'farmer_username': bill.farmer.username if bill.farmer else 'N/A',
        'total_amount': bill.total_amount,
        'paid_amount': bill.paid_amount,
        'amount_due': bill.amount_due,
        'due_date': bill.due_date,
        'bill_status': 'Approved' if bill.is_approved else 'Rejected',
    }
    if hasattr(settings, 'BASE_URL'):
        context['bill_detail_url'] = settings.BASE_URL + reverse('finance:bill_detail', args=[bill.pk])
    else:
        context['bill_detail_url'] = 'http://127.0.0.1:8000' + reverse('finance:bill_detail', args=[bill.pk])
    
    return send_general_notification_email(recipient_emails, subject, template, context)

def send_payment_reminder_email(bill, due_date_from_form=None):
    """Sends a payment reminder email to the farmer for a specific bill."""
    if not bill.farmer or not bill.farmer.email:
        print(f"WARNING: Cannot send payment reminder for Bill #{bill.pk}: No farmer email found.")
        return False
    
    effective_due_date = due_date_from_form or bill.due_date

    subject = f"Payment Reminder: Your Farm Shop Bill (ID: #{bill.pk})"
    template = 'users/notification_payment_reminder.html'
    context = {
        'bill_id': bill.pk,
        'farmer_username': bill.farmer.username,
        'total_amount': bill.total_amount,
        'amount_due': bill.amount_due,
        'due_date': effective_due_date,
    }
    if hasattr(settings, 'BASE_URL'):
        context['bill_detail_url'] = settings.BASE_URL + reverse('finance:bill_detail', args=[bill.pk])
    else:
        context['bill_detail_url'] = 'http://127.0.0.1:8000' + reverse('finance:bill_detail', args=[bill.pk])

    return send_general_notification_email([bill.farmer.email], subject, template, context)


def send_purchase_notification_email(purchase):
    """Sends an email to admins when a new purchase is recorded."""
    admin_emails = _get_admin_emails()
    if not admin_emails:
        print("WARNING: No active admin emails found to send new purchase notification.")
        return False

    subject = f"New Product Purchase Recorded (ID: #{purchase.pk})"
    template = 'users/notification_new_purchase.html'
    context = {
        'purchase_id': purchase.pk,
        'product_name': purchase.product.name,
        'quantity': purchase.quantity,
        'unit': purchase.product.unit,
        'total_cost': purchase.total_cost,
        'supplier_name': purchase.supplier.name if purchase.supplier else 'N/A',
        'purchase_date': purchase.purchase_date,
        'recorded_by_username': purchase.created_by.username if purchase.created_by else 'N/A',
    }
    if hasattr(settings, 'BASE_URL'):
        context['purchase_list_url'] = settings.BASE_URL + reverse('products:purchase_list')
    else:
        context['purchase_list_url'] = 'http://127.0.0.1:8000' + reverse('products:purchase_list')

    return send_general_notification_email(admin_emails, subject, template, context)

def send_sale_notification_email(sale):
    """Sends an email to admins when a new sale is recorded."""
    admin_emails = _get_admin_emails()
    if not admin_emails:
        print("WARNING: No active admin emails found to send new sale notification.")
        return False

    subject = f"New Product Sale Recorded (ID: #{sale.pk})"
    template = 'users/notification_new_sale.html'
    context = {
        'sale_id': sale.pk,
        'product_name': sale.product.name,
        'quantity': sale.quantity,
        'unit': sale.product.unit,
        'total_revenue': sale.total_revenue,
        'customer_username': sale.customer.username if sale.customer else 'N/A',
        'sale_date': sale.sale_date,
        'recorded_by_username': sale.created_by.username if sale.created_by else 'N/A',
    }
    if hasattr(settings, 'BASE_URL'):
        context['sale_list_url'] = settings.BASE_URL + reverse('products:sale_list')
    else:
        context['sale_list_url'] = 'http://127.0.0.1:8000' + reverse('products:sale_list')

    return send_general_notification_email(admin_emails, subject, template, context)

# --- START OF NEW ADDITION: Sale Receipt Email Notification ---

def send_sale_receipt_email(sale_obj, request=None):
    """Sends a sales receipt email to the customer if an email is available."""
    if not sale_obj.customer or not sale_obj.customer.email:
        print(f"WARNING: Cannot send sale receipt email for Sale #{sale_obj.pk}: No customer email found.")
        return False

    subject = f"Your Farm Shop Sale Receipt (ID: #{sale_obj.receipt_number})"
    template = 'users/notification_sale_receipt.html' # New email template for receipts
    
    context = {
        'sale': sale_obj,
        'customer_username': sale_obj.customer.username,
    }
    
    # Generate an absolute URL for the receipt detail/print view
    if request:
        context['receipt_view_url'] = request.build_absolute_uri(sale_obj.get_receipt_url())
    elif hasattr(settings, 'BASE_URL'):
        context['receipt_view_url'] = settings.BASE_URL + sale_obj.get_receipt_url()
    else:
        # Fallback for command line or if BASE_URL/request is unavailable
        context['receipt_view_url'] = 'http://127.0.0.1:8000' + sale_obj.get_receipt_url()
    
    return send_general_notification_email([sale_obj.customer.email], subject, template, context)

# --- END OF NEW ADDITION ---

# Twilio Messaging (Commented out for now)
# (Your Twilio functions here, as previously provided but commented)