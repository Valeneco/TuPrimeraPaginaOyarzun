from django import forms
from .models import Customer, CustomerInvoice, Vendor, VendorInvoice

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerInvoiceForm(forms.ModelForm):
    class Meta:
        model = CustomerInvoice
        # Excluimos created/updated
        exclude = ('created_at', 'updated_at') 
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}), # Incluimos el nuevo campo
        }


class VendorInvoiceForm(forms.ModelForm):
    class Meta:
        model = VendorInvoice
        # Excluimos created/updated
        exclude = ('created_at', 'updated_at') 
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class VendorForm(forms.ModelForm):
    """Formulario para crear un nuevo Proveedor."""
    class Meta:
        model = Vendor
        
        exclude = ('id', 'created_at', 'updated_at')
        
        labels = {
            'name': 'Vendor name',
            'address': 'Address',
            'email': 'E-mail',
            'tax_id': 'TAX ID',
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'email' : forms.EmailInput(attrs={'class': 'form-control'}), 

            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
        }