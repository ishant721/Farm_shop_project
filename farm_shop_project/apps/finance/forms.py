# farm_shop_project/apps/finance/forms.py
from django import forms
from .models import FarmerBill
from apps.users.models import CustomUser # To limit farmer choices in the form

class FarmerBillForm(forms.ModelForm):
    # Override farmer field to filter only users with user_type='farmer'
    farmer = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type='farmer', is_active=True).order_by('username'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Farmer"
    )

    class Meta:
        model = FarmerBill
        # Do NOT include created_by, is_approved, created_at, updated_at here.
        # created_by set automatically in view. is_approved handled by admin/view logic.
        fields = ['farmer', 'description', 'total_amount', 'paid_amount', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: Describe what the farmer bought (e.g., 5kg potatoes, 2 dozen eggs)'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # type="date" provides calendar picker
        }
        labels = {
            'total_amount': 'Total Bill Amount ($)',
            'paid_amount': 'Amount Paid ($)',
            'due_date': 'Payment Due Date',
        }

    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get('total_amount')
        paid_amount = cleaned_data.get('paid_amount')

        if total_amount is not None and paid_amount is not None:
            if paid_amount > total_amount:
                self.add_error('paid_amount', "Amount paid cannot be greater than the total amount.")
            if total_amount <= 0:
                self.add_error('total_amount', "Total amount must be greater than zero.")
        
        return cleaned_data