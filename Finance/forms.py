from django import forms
from accounts.models import CustomUser as User 
from .models import Customer, CustomerInvoice, Vendor, VendorInvoice

class CustomerUserForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Customer
        exclude = ('user', 'created_at', 'updated_at')

class VendorUserForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Vendor
        exclude = ('user', 'payment_date','created_at', 'updated_at')

class CustomerInvoiceForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # 1. Deshabilitar el campo 'customer' si no es Staff
        if 'customer' in self.fields and user and not user.is_staff:
            self.fields['customer'].disabled = True
            
            if hasattr(user, 'customer_profile'):
                self.fields['customer'].queryset = Customer.objects.filter(pk=user.customer_profile.pk)

    class Meta:
        model = CustomerInvoice
        # Lo incluimos para poder deshabilitarlo.
        fields = [
            'invoice_number', 
            'customer', 
            'due_date', 
            'amount', 
            'notes',
            'status',
        ]
        
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    # *** CORRECCIÓN CLAVE: Sobrescribir el clean_customer ***
    def clean_customer(self):
        """Asegura que el valor del Customer se mantenga si el campo estaba deshabilitado."""
        # Si el formulario está editando una instancia y el campo 'customer' no fue enviado
        # (porque estaba deshabilitado/ignorado por el navegador), usa el valor original (self.instance.customer).
        if self.instance and 'customer' in self.fields and self.fields['customer'].disabled:
             return self.instance.customer
             
        # Si el campo no estaba deshabilitado o si fue enviado correctamente, usa el valor limpio.
        return self.cleaned_data.get('customer')


class VendorInvoiceForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # 1. Deshabilitar el campo 'vendor' si no es Staff
        if 'vendor' in self.fields and user and not user.is_staff:
            self.fields['vendor'].disabled = True
            if hasattr(user, 'vendor_profile'):
                self.fields['vendor'].queryset = Vendor.objects.filter(pk=user.vendor_profile.pk)

    class Meta:
        model = VendorInvoice
        fields = [
            'invoice_number', 
            'vendor', 
            'due_date', 
            'amount', 
            'notes',
            'status'
            # Agrega los campos que uses, excluyendo 'date_issued', 'created_at', etc.
        ]
        
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    # *** CORRECCIÓN CLAVE: Sobrescribir el clean_vendor ***
    def clean_vendor(self):
        """Asegura que el valor del Vendor se mantenga si el campo estaba deshabilitado."""
        if self.instance and 'vendor' in self.fields and self.fields['vendor'].disabled:
            return self.instance.vendor
        return self.cleaned_data.get('vendor')