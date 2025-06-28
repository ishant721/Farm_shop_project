# apps/users/urls.py
from django.urls import path
from .views import (
    RegistrationView,
    OTPVerificationView,
    ResendOTPView,
    LoginView,
    LogoutView,
    ForgotPasswordView,
    PasswordResetDoneView,
    PasswordResetSetNewView,
    PasswordResetOTPVerifyView,
    PasswordResetCompleteView,
    UserProfileView,
    AdminEmployeeCreateView,
    AdminDashboardView,
    ToggleEmployeeStatusView,
    AdminNotificationView,
    FarmerSearchView # <--- NEW IMPORT
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'users'

urlpatterns = [
    # HTML-based Auth views
    path('register/', RegistrationView.as_view(), name='register'),
    path('verify-otp/', OTPVerificationView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Password reset views (OTP-based)
    path('password-reset/', ForgotPasswordView.as_view(), name='password_reset_request'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/verify-otp/', PasswordResetOTPVerifyView.as_view(), name='password_reset_otp_verify'),
    path('password-reset/set-new/', PasswordResetSetNewView.as_view(), name='password_reset_set_new'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Admin-specific employee management
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/create-employee/', AdminEmployeeCreateView.as_view(), name='admin_create_employee'),
    path('admin/employee/<int:pk>/toggle-status/', ToggleEmployeeStatusView.as_view(), name='toggle_employee_status'),
    
    # Admin Notification Bar URLs
    path('admin/notify-farmers/', AdminNotificationView.as_view(), name='admin_notify_farmers'),
    path('admin/search-farmers/', FarmerSearchView.as_view(), name='admin_search_farmers'), # <--- NEW URL

    # JWT Authentication (for API endpoints)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]