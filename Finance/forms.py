from django import forms
from .models import CustomerInvoice, VendorInvoice, Customer, Vendor

# ===============================
# CUSTOMER INVOICE FORM
# ===============================
class CustomerInvoiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Si el usuario no es staff y tiene customer_profile
        if user and not user.is_staff and hasattr(user, 'customer_profile'):
            # Limitar el dropdown a sí mismo
            self.fields['customer'].queryset = Customer.objects.filter(pk=user.customer_profile.pk)
            self.fields['customer'].disabled = False
            self.fields['customer'].initial = user.customer_profile

        # Seguridad: bloquear el status si no es staff
        if 'status' in self.fields and user and not user.is_staff:
            self.fields['status'].disabled = True

    class Meta:
        model = CustomerInvoice
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

    def clean_customer(self):
        """Asegura que siempre se retenga el customer correcto"""
        if self.instance and 'customer' in self.fields and not self.fields['customer'].disabled:
            return self.cleaned_data.get('customer')
        return self.instance.customer

    def clean_status(self):
        """Protege el status si el usuario no es staff"""
        if self.instance and 'status' in self.fields and self.fields['status'].disabled:
            return self.instance.status
        return self.cleaned_data.get('status')


# ===============================
# VENDOR INVOICE FORM
# ===============================
class VendorInvoiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Si el usuario no es staff y tiene vendor_profile
        if user and not user.is_staff and hasattr(user, 'vendor_profile'):
            # Limitar el dropdown a sí mismo
            self.fields['vendor'].queryset = Vendor.objects.filter(pk=user.vendor_profile.pk)
            self.fields['vendor'].disabled = False
            self.fields['vendor'].initial = user.vendor_profile
        else:
            # Staff puede ver todos los vendors
            self.fields['vendor'].queryset = Vendor.objects.all()

        # Seguridad: bloquear el status si no es staff
        if 'status' in self.fields and user and not user.is_staff:
            self.fields['status'].disabled = True

    class Meta:
        model = VendorInvoice
        fields = [
            'invoice_number',
            'vendor',
            'due_date',
            'amount',
            'notes',
            'status'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_vendor(self):
        """Asegura que siempre haya un vendor seleccionado"""
        vendor = self.cleaned_data.get('vendor')
        if not vendor:
            raise forms.ValidationError("Vendor is required.")
        return vendor

    def clean_status(self):
        """Protege el status si el usuario no es staff"""
        if self.instance and 'status' in self.fields and self.fields['status'].disabled:
            return self.instance.status
        return self.cleaned_data.get('status')
