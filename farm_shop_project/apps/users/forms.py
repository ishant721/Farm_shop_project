# apps/users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import authenticate
from phonenumber_field.formfields import PhoneNumberField

# Placeholder for CustomUser to allow forms.py to be linted alone
try:
    from .models import CustomUser
except ImportError:
    class CustomUser(object):
        objects = None
        def set_password(self, password): pass
        def check_password(self, password): return True
        def __str__(self): return "MockUser"
        is_active = True
        username = "mockuser"
        email = "mock@example.com"
        user_type = "farmer"
        @staticmethod
        def make_random_password():
            import random
            import string
            length = 12
            chars = string.ascii_letters + string.digits + string.punctuation
            return ''.join(random.choice(chars) for i in range(length))


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'id_password_reg', 'placeholder': 'Password'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), label='Confirm Password')
    email = forms.EmailField(required=True, label='Email Address',
                             widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    username = forms.CharField(required=True, max_length=150, label='Username',
                               widget=forms.TextInput(attrs={'placeholder': 'Choose a Username'}))

    phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +12125552368'}),
        required=False,
        label='Phone Number'
    )

    user_type = forms.ChoiceField(
        choices=[
            ('farmer', 'Farmer'),
            ('business', 'Business Client'),
        ],
        label='Register As',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label='Date of Birth'
    )

    address_line1 = forms.CharField(max_length=255, required=False, label="Address Line 1",
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'House/Flat No., Building Name'}))
    address_line2 = forms.CharField(max_length=255, required=False, label="Address Line 2 (Optional)",
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Name, Locality'}))
    pincode = forms.CharField(max_length=10, required=False, label="Pincode",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 400001', 'id': 'id_pincode_reg'}))
    city = forms.CharField(max_length=100, required=False, label="City",
                           widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'placeholder': 'Auto-filled by Pincode', 'id': 'id_city_reg'}))
    state = forms.CharField(max_length=100, required=False, label="State",
                            widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'placeholder': 'Auto-filled by Pincode', 'id': 'id_state_reg'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'date_of_birth',
                  'address_line1', 'address_line2', 'pincode', 'city', 'state',
                  'user_type', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['password', 'password2', 'user_type', 'date_of_birth', 'city', 'state']:
                field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        self.fields['password2'].widget.attrs['data-password-toggle'] = 'false'


    def clean_username(self):
        username = self.cleaned_data['username']
        if hasattr(CustomUser, 'objects') and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if hasattr(CustomUser, 'objects') and CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode and not pincode.isdigit():
            raise forms.ValidationError("Pincode must contain only digits.")
        return pincode

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'id_password_login', 'placeholder': 'Password', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Username or Email"

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username or not password:
            raise forms.ValidationError("Please enter a username/email and password.")

        self.user_cache = authenticate(username=username, password=password)

        if self.user_cache is None:
            if hasattr(CustomUser, 'objects'):
                try:
                    user = CustomUser.objects.get(email__iexact=username)
                    if user.check_password(password):
                        self.user_cache = user
                    else:
                        raise forms.ValidationError("Invalid username/email or password.", code='invalid_login')
                except CustomUser.DoesNotExist:
                    raise forms.ValidationError("Invalid username/email or password.", code='invalid_login')
            else:
                raise forms.ValidationError("Invalid username/email or password.", code='invalid_login')
        
        if self.user_cache and not self.user_cache.is_active:
            raise forms.ValidationError(
                "Your account is not active. Please verify your email.",
                code='inactive_account'
            )
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6, label="Verification Code",
                          widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit OTP', 'class': 'form-control'}))


class ForgotPasswordForm(PasswordResetForm):
    email = forms.EmailField(required=True, label="Enter your registered email address",
                             widget=forms.EmailInput(attrs={'placeholder': 'Your Email Address', 'class': 'form-control'}))

    def get_users(self, email):
        if hasattr(CustomUser, 'objects'):
            active_users = CustomUser.objects.filter(email__iexact=email, is_active=True)
            return (u for u in active_users if u.has_usable_password())
        return []


class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'id': 'id_new_password1', 'class': 'form-control'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'data-password-toggle': 'false'}),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password2'].widget.attrs['data-password-toggle'] = 'false'


class EmployeeCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth',
                  'address_line1', 'address_line2', 'pincode', 'city', 'state']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        self.fields['username'].widget.attrs['placeholder'] = 'Employee Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Employee Email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'e.g., +12125552368'
        self.fields['address_line1'].widget.attrs['placeholder'] = 'House/Flat No., Building Name'
        self.fields['address_line2'].widget.attrs['placeholder'] = 'Street Name, Locality'
        self.fields['pincode'].widget.attrs['placeholder'] = 'e.g., 400001'

        self.fields['date_of_birth'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        
        self.fields['city'].widget.attrs['readonly'] = 'readonly'
        self.fields['city'].widget.attrs['placeholder'] = 'Auto-filled by Pincode'
        self.fields['state'].widget.attrs['readonly'] = 'readonly'
        self.fields['state'].widget.attrs['placeholder'] = 'Auto-filled by Pincode'

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode and not pincode.isdigit():
            raise forms.ValidationError("Pincode must contain only digits.")
        return pincode

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employee'
        user.is_active = True

        random_password = CustomUser.make_random_password()
        user.set_password(random_password)

        if commit:
            user.save()
        
        return user, random_password


# --- NotificationForm (moved here from views.py) ---
# This form needs to be outside AdminNotificationView to be imported by AdminNotificationView.get_form_class()
class NotificationForm(forms.Form):
    # This field will be populated by the frontend search/selection via JavaScript
    selected_farmer_ids = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'id_selected_farmer_ids'}),
        required=False # Allow sending to all if blank
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Subject"
    )
    message_body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label="Message Content"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No longer populating choices here, JS handles dynamic display and hidden input
        self.fields['subject'].widget.attrs.update({'class': 'form-control'})
        self.fields['message_body'].widget.attrs.update({'class': 'form-control'})