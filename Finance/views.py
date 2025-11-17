from datetime import date 
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import CustomerInvoiceForm, VendorInvoiceForm
from .models import Customer, CustomerInvoice, Vendor, VendorInvoice

# === UTILIDADES ===
def staff_required(view_func):
    """Decorator para restringir vista solo a staff/admin"""
    decorated_view_func = user_passes_test(lambda u: u.is_staff, login_url='login')(view_func)
    return decorated_view_func

# === BASE VIEWS ===
def index(request):
    return render(request, "Finance/home.html")

def test(request):
    return render(request, "Finance/test.html")

# === REDIRECT TO ACCOUNTS SIGNUP ===
@login_required
@staff_required
def add_customer(request):
    messages.info(request, "Please use the Accounts signup page to create a customer.")
    return redirect('signup')  # accounts/signup/

@login_required
@staff_required
def add_vendor(request):
    messages.info(request, "Please use the Accounts signup page to create a vendor.")
    return redirect('signup')  # accounts/signup/

# === INVOICE MANAGEMENT ===
@login_required
def add_customer_invoice(request):
    if request.method == "POST":
        form = CustomerInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.date_issued = date.today()
            invoice.save()
            messages.success(request, "Customer invoice created successfully!")
            return redirect("profile")
    else:
        form = CustomerInvoiceForm()
    return render(request, "Finance/customer_invoice_form.html", {'form': form, 'page_title': 'Add Customer Invoice (AR)'})

@login_required
def add_vendor_invoice(request):
    if request.method == "POST":
        form = VendorInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.date_issued = date.today()
            invoice.save()
            messages.success(request, "Vendor invoice created successfully!")
            return redirect("profile")
    else:
        form = VendorInvoiceForm()
    return render(request, "Finance/vendor_invoice_form.html", {'form': form, 'page_title': 'Add Vendor Invoice (AP)'})

@login_required
def invoice_list(request):
    invoices = CustomerInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    return render(request, "Finance/invoice_list.html", {'invoices': invoices, 'page_title': 'Outstanding AR Invoices'})

@login_required
def vendor_payment_list(request):
    invoices = VendorInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    return render(request, "Finance/vendor_invoice_list.html", {'invoices': invoices, 'page_title': 'Pending AP Payments'})

# === SEARCH VIEWS ===
@login_required
def search_customers(request):
    query = request.GET.get('q')
    customers = Customer.objects.filter(Q(name__icontains=query) | Q(company_code__icontains=query)).order_by('name') if query else None
    return render(request, "Finance/search_customer.html", {'customers': customers, 'query': query, 'page_title': 'Search Customers'})

@login_required
def search_vendors(request):
    query = request.GET.get('q')
    vendors = Vendor.objects.filter(Q(name__icontains=query) | Q(company_code__icontains=query)).order_by('name') if query else None
    return render(request, "Finance/search_vendor.html", {'vendors': vendors, 'query': query, 'page_title': 'Search Vendors'})

# === ADMIN HOME VIEWS ===
# Comentadas para desactivar dashboard propio y usar solo Django Admin
"""
@login_required
@staff_required
def pending_ar_list(request):
    invoices = CustomerInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    return render(request, 'Finance/invoice_list.html', {'invoices': invoices, 'page_title': 'Pending AR Invoices'})

@login_required
@staff_required
def pending_ap_list(request):
    invoices = VendorInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    return render(request, "Finance/vendor_invoice_list.html", {'invoices': invoices, 'page_title': 'Pending AP Payments'})
"""
