from django import forms
from django.contrib.auth.models import User
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
        exclude = ('user', 'created_at', 'updated_at')

class CustomerInvoiceForm(forms.ModelForm):
    class Meta:
        model = CustomerInvoice
        exclude = ('created_at', 'updated_at') 
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class VendorInvoiceForm(forms.ModelForm):
    class Meta:
        model = VendorInvoice
        exclude = ('created_at', 'updated_at') 
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
