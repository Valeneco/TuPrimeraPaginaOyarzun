from django.contrib import admin
from .models import Customer, Vendor, CustomerInvoice, VendorInvoice

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company_code', 'created_at')
    search_fields = ('name', 'email', 'company_code')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'company_code', 'created_at')
    search_fields = ('name', 'email', 'company_code')

@admin.register(CustomerInvoice)
class CustomerInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'date_issued', 'due_date', 'amount', 'status')
    list_filter = ('status', 'date_issued')
    search_fields = ('invoice_number', 'customer__name')

@admin.register(VendorInvoice)
class VendorInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'vendor', 'date_issued', 'due_date', 'amount', 'status')
    list_filter = ('status', 'date_issued')
    search_fields = ('invoice_number', 'vendor__name')
