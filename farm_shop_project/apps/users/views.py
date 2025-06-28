# apps/users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import View, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.db.models import Q
from django.db import models
from django.conf import settings

# For Pincode Lookup API
from django.http import JsonResponse
import requests
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django import forms
from django.core.mail import send_mail
from django.template.loader import render_to_string


# Import your forms and models
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    OTPVerificationForm,
    ForgotPasswordForm,
    SetNewPasswordForm,
    EmployeeCreationForm,
    NotificationForm # Ensure NotificationForm is imported
)
from .models import CustomUser, OneTimePassword
from .utils import (
    create_and_send_otp,
    send_password_reset_otp_email,
    send_employee_credentials_email,
    send_new_farmer_registration_email
)


class RegistrationView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:verify_otp')

    def form_valid(self, form):
        user = form.save(commit=True)
        otp_sent = create_and_send_otp(user, otp_type='registration', request=self.request)

        if otp_sent:
            messages.success(self.request, "Registration successful! A verification code has been sent to your email. Please verify your account.")
            self.request.session['unverified_email'] = user.email
            
            if user.user_type == 'farmer':
                send_new_farmer_registration_email(user)

            return super().form_valid(form)
        else:
            user.delete()
            messages.error(self.request, "Failed to send verification email. Please try again.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.replace('_', ' ').title()}: {error}")
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)


class OTPVerificationView(FormView):
    template_name = 'users/otp_verification.html'
    form_class = OTPVerificationForm
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        self.unverified_email = request.session.get('unverified_email')
        if not self.unverified_email:
            messages.error(request, "No email found for verification. Please register first.")
            return redirect('users:register')
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        otp_code = form.cleaned_data['otp']
        unverified_email = self.request.session.get('unverified_email')

        if not unverified_email:
            messages.error(self.request, "Verification session expired or invalid. Please register again.")
            return redirect('users:register')

        try:
            otp_instance = OneTimePassword.objects.filter(
                models.Q(email__iexact=unverified_email) | models.Q(user__email__iexact=unverified_email),
                otp=otp_code,
                otp_type='registration',
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()

            if otp_instance:
                user = CustomUser.objects.filter(email__iexact=unverified_email).first()
                if user:
                    user.is_active = True
                    user.save()
                    otp_instance.is_used = True
                    otp_instance.save()
                    del self.request.session['unverified_email']
                    messages.success(self.request, "Email verified successfully! You can now log in.")
                    return super().form_valid(form)
                else:
                    messages.error(self.request, "User not found for this email. Please register again.")
                    return self.form_invalid(form)
            else:
                messages.error(self.request, "Invalid or expired OTP. Please try again or request a new one.")
                return self.form_invalid(form)

        except CustomUser.DoesNotExist:
            messages.error(self.request, "User not found. Please register again.")
            return redirect('users:register')
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.replace('_', ' ').title()}: {error}")
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)


class ResendOTPView(View):
    def post(self, request, *args, **kwargs):
        unverified_email = request.session.get('unverified_email')
        if unverified_email:
            user = CustomUser.objects.filter(email__iexact=unverified_email).first()
            if user and user.is_active:
                messages.info(request, "Your account is already active. Please log in.")
                return redirect('users:login')

            otp_sent = create_and_send_otp(user if user else unverified_email, otp_type='registration', request=request)
            if otp_sent:
                messages.success(request, "A new verification code has been sent to your email.")
            else:
                messages.error(request, "Failed to resend OTP. Please try again.")
        else:
            messages.error(request, "No email found for OTP resend. Please register first.")
            return redirect('users:register')
        return redirect('users:verify_otp')


class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser or user.user_type == 'admin':
                return reverse_lazy('users:admin_dashboard')
            return reverse_lazy('dashboards:dashboard_redirect')
        return reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.get_user()
        if user.is_superuser or user.is_staff:
            if not user.is_active:
                user.is_active = True
                user.save()
            login(self.request, user)
            messages.success(self.request, f"Welcome, {user.username}!")
            return super().form_valid(form)
        
        login(self.request, user)
        messages.success(self.request, f"Welcome, {user.username}!")
        return super().form_valid(form)


    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.replace('_', ' ').title()}: {error}")
        
        if 'inactive_account' in [e.code for e in form.errors.as_data().get('__all__', [])]:
            login_identifier = form.cleaned_data.get('username')
            user_to_check = CustomUser.objects.filter(username__iexact=login_identifier).first() or \
                            CustomUser.objects.filter(email__iexact=login_identifier).first()

            if user_to_check and (user_to_check.is_superuser or user_to_check.is_staff):
                if not user_to_check.is_active:
                    user_to_check.is_active = True
                    user_to_check.save()
                login(self.request, user_to_check)
                messages.success(self.request, f"Welcome, {user_to_check.username}!")
                return redirect(self.get_success_url())
            elif user_to_check and not user_to_check.is_active:
                messages.warning(self.request, "Your account is not active. Please verify your email to log in.")
                self.request.session['unverified_email'] = user_to_check.email
                return redirect('users:verify_otp')
            else:
                messages.error(self.request, "Invalid username/email or password.")
        else:
            for error in form.non_field_errors():
                messages.error(self.request, error)
        return super().form_invalid(form)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect(settings.LOGOUT_REDIRECT_URL)


class ForgotPasswordView(FormView):
    template_name = 'users/password_reset_request.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('users:password_reset_otp_verify')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = CustomUser.objects.get(email__iexact=email)
            if user.is_active:
                otp_sent = send_password_reset_otp_email(user)
                if otp_sent:
                    messages.success(self.request, "A password reset code has been sent to your email. Please check your inbox to continue.")
                    self.request.session['password_reset_email'] = user.email
                else:
                    messages.error(self.request, "Failed to send password reset code. Please try again.")
                    return self.form_invalid(form)
            else:
                 messages.warning(self.request, "This account is not active. Please verify your email first.")
                 self.request.session['unverified_email'] = user.email
                 return redirect('users:verify_otp')

        except CustomUser.DoesNotExist:
            messages.success(self.request, "If an account with that email exists, we've sent a password reset code to your email.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.replace('_', ' ').title()}: {error}")
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)


class PasswordResetDoneView(TemplateView):
    template_name = 'users/password_reset_done.html'


class PasswordResetOTPVerifyView(FormView):
    template_name = 'users/password_reset_otp_verify.html'
    form_class = OTPVerificationForm
    success_url = reverse_lazy('users:password_reset_set_new')

    def dispatch(self, request, *args, **kwargs):
        self.password_reset_email = request.session.get('password_reset_email')
        if not self.password_reset_email:
            messages.error(request, "Password reset session expired or invalid. Please request a new password reset.")
            return redirect('users:password_reset_request')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        otp_code = form.cleaned_data['otp']
        password_reset_email = self.request.session.get('password_reset_email')

        if not password_reset_email:
            messages.error(self.request, "Verification session expired or invalid. Please request a new password reset.")
            return redirect('users:password_reset_request')
        
        try:
            otp_instance = OneTimePassword.objects.filter(
                models.Q(email__iexact=password_reset_email) | models.Q(user__email__iexact=password_reset_email),
                otp=otp_code,
                otp_type='password_reset',
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()

            if otp_instance:
                user = CustomUser.objects.filter(email__iexact=password_reset_email).first()
                if user:
                    otp_instance.is_used = True
                    otp_instance.save()
                    self.request.session['password_reset_user_id'] = user.pk
                    del self.request.session['password_reset_email']
                    messages.success(self.request, "Code verified successfully! You can now set your new password.")
                    return super().form_valid(form)
                else:
                    messages.error(self.request, "User not found for this email. Please request a new password reset.")
                    return self.form_invalid(form)
            else:
                messages.error(self.request, "Invalid or expired reset code. Please try again or request a new one.")
                return self.form_invalid(form)

        except Exception as e:
            logger.error(f"Error during OTP verification for {password_reset_email}: {e}")
            messages.error(self.request, f"An unexpected error occurred during OTP verification.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.replace('_', ' ').title()}: {error}")
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)


class PasswordResetSetNewView(FormView):
    template_name = 'users/password_reset_set_new.html'
    form_class = SetNewPasswordForm
    success_url = reverse_lazy('users:password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('password_reset_user_id')
        if not user_id:
            messages.error(request, "Password reset session expired or invalid. Please request a new password reset.")
            return redirect('users:password_reset_request')
        
        try:
            self.user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found. Please request a new password reset.")
            return redirect('users:password_reset_request')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        del self.request.session['password_reset_user_id']
        messages.success(self.request, "Your password has been reset successfully. You can now log in with your new password.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.replace('_', ' ').title()}: {error}")
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)


class PasswordResetCompleteView(TemplateView):
    template_name = 'users/password_reset_complete.html'


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AdminEmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'users/admin_create_employee.html'
    form_class = EmployeeCreationForm
    success_url = reverse_lazy('users:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page.")
        return redirect('dashboards:dashboard_redirect')

    def form_valid(self, form):
        user, raw_password = form.save()

        email_sent = send_employee_credentials_email(user, raw_password, self.request)

        if email_sent:
            messages.success(self.request, f"Employee '{user.username}' created successfully and credentials sent to {user.email}.")
        else:
            messages.warning(self.request, f"Employee '{user.username}' created, but failed to send credentials email to {user.email}. Please provide credentials manually.")
            
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field.replace('_', ' ').title()}: {error}")
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'users/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access the admin dashboard.")
        return redirect('dashboards:dashboard_redirect')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = CustomUser.objects.filter(
            models.Q(user_type='employee') | models.Q(user_type='farmer_employee'),
            is_superuser=False
        ).order_by('username')

        context['total_users_count'] = CustomUser.objects.count()
        context['active_employees_count'] = context['employees'].filter(is_active=True).count()

        return context

class ToggleEmployeeStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Toggles the is_active status of an employee account.
    Accessed by admin dashboard.
    """
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to perform this action.")
        return redirect('dashboards:dashboard_redirect')

    def post(self, request, pk, *args, **kwargs):
        employee = get_object_or_404(CustomUser, pk=pk)

        if employee == request.user or employee.is_superuser:
            messages.error(request, "Cannot toggle status for yourself or a superuser via this method.")
            return redirect(reverse_lazy('users:admin_dashboard'))

        if employee.user_type not in ['employee', 'farmer_employee']:
            messages.error(request, "Invalid user type for this action.")
            return redirect(reverse_lazy('users:admin_dashboard'))

        employee.is_active = not employee.is_active
        employee.save()

        status_message = "activated" if employee.is_active else "deactivated (banned)"
        messages.success(request, f"Employee '{employee.username}' has been {status_message}.")

        return redirect(reverse_lazy('users:admin_dashboard'))


class AdminNotificationView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'users/admin_notification_bar.html'
    form_class = NotificationForm # Use the form from forms.py
    success_url = reverse_lazy('users:admin_dashboard')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to send notifications.")
        return redirect('dashboards:dashboard_redirect')

    def form_valid(self, form):
        selected_farmer_ids_str = form.cleaned_data['selected_farmer_ids']
        subject = form.cleaned_data['subject']
        message_body = form.cleaned_data['message_body']

        if selected_farmer_ids_str:
            recipients_pks = [int(pk) for pk in selected_farmer_ids_str.split(',') if pk.isdigit()]
            farmers = CustomUser.objects.filter(pk__in=recipients_pks, user_type__in=['farmer', 'farmer_employee'], is_active=True)
        else:
            farmers = CustomUser.objects.filter(user_type__in=['farmer', 'farmer_employee'], is_active=True)

        sent_count = 0
        total_farmers_to_notify = farmers.count()

        if total_farmers_to_notify == 0:
            messages.warning(self.request, "No active farmers found (or selected) to send notifications.")
            return self.form_invalid(form)

        for farmer in farmers:
            if farmer.email:
                context = {
                    'admin_username': self.request.user.username,
                    'farmer_username': farmer.username,
                    'subject_line': subject,
                    'message_content': message_body,
                    'site_name': settings.JAZZMIN_SETTINGS.get('site_header', 'Farm Shop'),
                }
                email_sent = self._send_notification_email(
                    recipient_email=farmer.email,
                    subject=subject,
                    template_name='users/notification_admin_to_farmer_email.html',
                    context=context
                )
                if email_sent:
                    sent_count += 1

        if sent_count > 0:
            messages.success(self.request, f"Successfully sent email notifications to {sent_count} out of {total_farmers_to_notify} farmers.")
        else:
            messages.warning(self.request, "No email notifications were sent. Check farmer emails or email settings.")

        return super().form_valid(form)

    def _send_notification_email(self, recipient_email, subject, template_name, context):
        """Helper to send a single notification email."""
        try:
            html_message = render_to_string(template_name, context)
            plain_message = f"{subject}\n\n{context.get('message_content', '')}"
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                html_message=html_message,
                fail_silently=False
            )
            return True
        except Exception as e:
            logger.error(f"Error sending notification email to {recipient_email}: {e}")
            return False


# --- Pincode Lookup API View ---
class PincodeLookupView(View):
    def get(self, request, *args, **kwargs):
        pincode = request.GET.get('pincode')
        logger.debug(f"Pincode lookup requested for: {pincode}")

        if not pincode or not pincode.isdigit() or len(pincode) != 6:
            logger.warning(f"Invalid pincode format received: {pincode}")
            return JsonResponse({'status': 'error', 'message': 'Invalid pincode format.'}, status=400)

        api_url = f"https://api.postalpincode.in/pincode/{pincode}"

        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Pincode API raw response for {pincode}: {data}")

            if data and isinstance(data, list) and len(data) > 0 and data[0]['Status'] == 'Success':
                post_offices = data[0]['PostOffice']
                if post_offices:
                    city = post_offices[0]['District']
                    state = post_offices[0]['State']
                    logger.info(f"Pincode {pincode} found: City={city}, State={state}")
                    return JsonResponse({'status': 'success', 'city': city, 'state': state})
                else:
                    logger.warning(f"No post offices found for pincode {pincode}.")
                    return JsonResponse({'status': 'error', 'message': 'No post offices found for this pincode.'})
            else:
                error_message = data[0].get('Message', 'Invalid Pincode or no data found.') if data and isinstance(data, list) and len(data) > 0 else 'Unexpected API response format.'
                logger.warning(f"Pincode API returned error status for {pincode}: {error_message}")
                return JsonResponse({'status': 'error', 'message': error_message})

        except requests.exceptions.Timeout:
            logger.error(f"Pincode lookup for {pincode} timed out after 10 seconds.")
            return JsonResponse({'status': 'error', 'message': 'API request timed out.'}, status=504)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Pincode lookup connection error for {pincode}: {e}")
            return JsonResponse({'status': 'error', 'message': 'Could not connect to pincode API. Check internet/firewall.'}, status=503)
        except requests.exceptions.RequestException as e:
            logger.error(f"Pincode lookup request failed for {pincode}: {e}")
            return JsonResponse({'status': 'error', 'message': f'Pincode API request failed: {e}.'}, status=503)
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Pincode API response parsing error for {pincode}: {e} - Data: {data}")
            return JsonResponse({'status': 'error', 'message': 'Error parsing API response. API format may have changed.'}, status=500)
        except Exception as e:
            logger.critical(f"An unexpected error occurred in PincodeLookupView for {pincode}: {e}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)


# --- Farmer Search API View for Admin Notification ---
class FarmerSearchView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.user_type == 'admin'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        if not query:
            return JsonResponse({'status': 'success', 'farmers': []})

        farmers_queryset = CustomUser.objects.filter(
            # --- START OF CHANGE ---
            (Q(user_type='farmer') | Q(user_type='farmer_employee')) & # Combine user types with AND
            Q(is_active=True) & # Ensure active users
            (Q(username__icontains=query) | # Combine search fields with OR
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query))
            # --- END OF CHANGE ---
        ).order_by('username')[:20]

        farmers_data = []
        for farmer in farmers_queryset:
            farmers_data.append({
                'id': farmer.pk,
                'username': farmer.username,
                'email': farmer.email,
                'full_name': farmer.get_full_name() or farmer.username
            })
        
        return JsonResponse({'status': 'success', 'farmers': farmers_data})