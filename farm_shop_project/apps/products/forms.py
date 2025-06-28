# farm_shop_project/apps/products/forms.py
from django import forms
from .models import Product, Supplier, Purchase, Sale
from apps.users.models import CustomUser


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'unit', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., kg, piece, dozen'}),
        }
        labels = {
            'name': 'Product Name',
            'description': 'Description',
            'price': 'Selling Price ($)',
            'stock': 'Current Stock',
            'unit': 'Unit Type',
            'image': 'Product Image',
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Price must be a positive number.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone_number', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +919876543210'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Supplier Address'}),
        }

class PurchaseForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Product"
    )
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Supplier",
        required=False
    )
    purchase_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Purchase Date'
    )

    class Meta:
        model = Purchase
        fields = ['product', 'supplier', 'quantity', 'unit_cost', 'purchase_date']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }
        labels = {
            'quantity': 'Quantity Purchased',
            'unit_cost': 'Cost Per Unit ($)',
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        return quantity

    def clean_unit_cost(self):
        unit_cost = self.cleaned_data['unit_cost']
        if unit_cost <= 0:
            raise forms.ValidationError("Unit cost must be a positive number.")
        return unit_cost

class SaleForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_approved=True, stock__gt=0).order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Product"
    )
    customer = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(user_type__in=['farmer', 'business', 'employee', 'admin']).order_by('username'), # Added 'admin' to customer types
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Customer",
        required=False
    )
    sale_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Sale Date'
    )

    class Meta:
        model = Sale
        # Add gst_rate here. Calculated fields will be set by the model's save method.
        fields = ['product', 'customer', 'quantity', 'unit_price', 'gst_rate', 'sale_date'] # <--- UPDATED FIELDS
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            # --- START OF NEW ADDITION ---
            'gst_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            # --- END OF NEW ADDITION ---
        }
        labels = {
            'quantity': 'Quantity Sold',
            'unit_price': 'Selling Price Per Unit ($)',
            # --- START OF NEW ADDITION ---
            'gst_rate': 'GST Rate (%)',
            # --- END OF NEW ADDITION ---
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive number.")
        
        # Check if enough stock is available (only for new sales, not edits)
        # For edits, more complex logic is needed for partial quantities/stock adjustment
        if self.instance.pk is None: # Only for new sales
            product = self.cleaned_data.get('product')
            if product and quantity > product.stock:
                raise forms.ValidationError(f"Not enough stock available. Only {product.stock} {product.unit} of {product.name} left.")
        
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data['unit_price']
        if unit_price <= 0:
            raise forms.ValidationError("Selling price must be a positive number.")
        return unit_price
    
    def clean_gst_rate(self): # <--- NEW CLEAN METHOD
        gst_rate = self.cleaned_data['gst_rate']
        if gst_rate < 0:
            raise forms.ValidationError("GST rate cannot be negative.")
        return gst_rate