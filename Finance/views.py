from datetime import date 
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist # Importar explícitamente

from .forms import CustomerInvoiceForm, VendorInvoiceForm
from .models import Customer, CustomerInvoice, Vendor, VendorInvoice

# === UTILITIES ===
def staff_required(view_func):
    """Decorator to restrict view only to staff/admin"""
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

# === INVOICE MANAGEMENT (CREATE) ===
@login_required
def add_customer_invoice(request):
    if getattr(request.user, 'user_type', None) != 'C':
        messages.error(request, "You are not authorized to create this type of invoice.")
        return redirect('profile') 
        
    form_kwargs = {'user': request.user}

    if request.method == "POST":
        form = CustomerInvoiceForm(request.POST, **form_kwargs)
        if form.is_valid():
            invoice = form.save(commit=False)
            
            try:
                # Usamos request.user.customer_profile y manejamos la excepción ObjectDoesNotExist
                invoice.customer = request.user.customer_profile
            except ObjectDoesNotExist:
                 messages.error(request, "Error: Customer profile link missing.")
                 return redirect('profile')

            invoice.date_issued = date.today()
            invoice.status = 'OUTSTANDING'
            
            invoice.save()
            
            messages.success(request, "Customer invoice created successfully!")
            return redirect("profile")
            
        else:
            print("=========================================")
            print("INVALID FORM. ERRORES DETECTADOS:")
            print(form.errors) 
            print("=========================================")
            messages.error(request, "Error: Please correct the marked fields.")
            
    else:
        form = CustomerInvoiceForm(**form_kwargs)
        
    return render(request, "Finance/customer_invoice_form.html", {'form': form, 'page_title': 'Add Customer Invoice (AR)'})

@login_required
def add_vendor_invoice(request):
    if getattr(request.user, 'user_type', None) != 'V' and not request.user.is_staff:
        messages.error(request, "You are not authorized to create this type of invoice.")
        return redirect('profile') 
    
    form_kwargs = {'user': request.user}
        
    if request.method == "POST":
        form = VendorInvoiceForm(request.POST, **form_kwargs)
        if form.is_valid():
            invoice = form.save(commit=False)
            
            # *** BLOQUE DE ASIGNACIÓN ESTABLE DEL VENDOR ***
            if request.user.user_type == 'V' and not request.user.is_staff:
                try:
                    # Usamos la sintaxis simple de acceso a la relación inversa
                    invoice.vendor = request.user.vendor_profile 
                    
                except ObjectDoesNotExist:
                    # Esta excepción se lanza si CustomUser no tiene un VendorProfile asociado
                    messages.error(request, "Error: Vendor profile not linked to user. Please ensure your profile exists.")
                    return redirect('profile')
                except Exception as e:
                    # Para capturar cualquier otro error inesperado en la asignación
                    print(f"Vendor assignment error: {e}") 
                    messages.error(request, "Error: Failed to link vendor profile.")
                    return redirect('profile')
            # **********************************************
            
            invoice.date_issued = date.today()
            
            if request.user.user_type == 'V' and not request.user.is_staff:
                invoice.status = 'OUTSTANDING'
            
            invoice.save()
            messages.success(request, "Vendor invoice created successfully!")
            return redirect("profile")
        else:
            print("=========================================")
            print("INVALID FORM. ERRORES DETECTADOS:")
            print(form.errors) 
            print("=========================================")
            messages.error(request, "Error: Please correct the marked fields.")

    else:
        form = VendorInvoiceForm(**form_kwargs)
        
    return render(request, "Finance/vendor_invoice_form.html", {'form': form, 'page_title': 'Add Vendor Invoice (AP)'})

# === INVOICE MANAGEMENT (READ LIST & DETAIL) ===
@login_required
def invoice_list(request):
    if request.user.is_staff:
        invoices = CustomerInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    elif request.user.user_type == 'C':
        try:
            customer = request.user.customer_profile
            invoices = CustomerInvoice.objects.filter(customer=customer).order_by('-date_issued')
        except ObjectDoesNotExist:
            invoices = CustomerInvoice.objects.none()
            messages.warning(request, "Customer profile not found.")
    else:
        invoices = CustomerInvoice.objects.none()

    return render(request, "Finance/invoice_list.html", {'invoices': invoices, 'page_title': 'Outstanding AR Invoices'})

@login_required
def vendor_payment_list(request):
    if request.user.is_staff:
        invoices = VendorInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    elif request.user.user_type == 'V':
        try:
            vendor = request.user.vendor_profile
            invoices = VendorInvoice.objects.filter(vendor=vendor).order_by('-date_issued')
        except ObjectDoesNotExist:
            invoices = VendorInvoice.objects.none()
            messages.warning(request, "Vendor profile not found.")
    else:
        invoices = VendorInvoice.objects.none()

    return render(request, "Finance/vendor_invoice_list.html", {'invoices': invoices, 'page_title': 'Pending AP Payments'})


@login_required
def invoice_detail(request, pk):
    
    invoice = None
    invoice_type = None
    related_user_profile = None 

    try:
        invoice = CustomerInvoice.objects.get(pk=pk)
        invoice_type = 'customer'
        related_user_profile = invoice.customer 
    except CustomerInvoice.DoesNotExist:
        try:
            invoice = VendorInvoice.objects.get(pk=pk)
            invoice_type = 'vendor'
            related_user_profile = invoice.vendor
        except VendorInvoice.DoesNotExist:
            raise Http404("Invoice does not exist.") 

    is_authorized = request.user.is_staff 
    
    owner_profile = getattr(request.user, invoice_type + '_profile', None) 
    is_owner = related_user_profile and owner_profile and related_user_profile == owner_profile

    if is_owner:
        is_authorized = True

    can_edit = is_authorized 
    
    if not is_authorized:
        messages.error(request, "You are not authorized to view this invoice.")
        return redirect('profile')

    context = {
        'invoice': invoice,
        'invoice_type': invoice_type,
        'page_title': f"Invoice Detail: {invoice.invoice_number}",
        'can_edit': can_edit, 
    }
    return render(request, "Finance/invoice_detail.html", context)


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


# ==================================
# === UPDATE (Edit) VIEWS ====
# ==================================

@login_required
def edit_customer_invoice(request, pk):
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    is_owner = False
    customer_profile = getattr(request.user, 'customer_profile', None)
    if customer_profile and invoice.customer == customer_profile:
        is_owner = True
        
    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to edit this invoice.")
        return redirect('profile')
    
    form_kwargs = {'instance': invoice, 'user': request.user}
    
    if request.method == "POST":
        form = CustomerInvoiceForm(request.POST, **form_kwargs)
        if form.is_valid():
            form.save() 
            messages.success(request, f"Customer Invoice AR-{invoice.invoice_number} updated successfully.")
            return redirect("profile")
    else:
        form = CustomerInvoiceForm(**form_kwargs) 
        
    context = {'form': form, 'page_title': f'Edit Customer Invoice AR-{invoice.invoice_number}'}
    return render(request, "Finance/customer_invoice_form.html", context)


@login_required
def edit_vendor_invoice(request, pk):
    invoice = get_object_or_404(VendorInvoice, pk=pk)
    
    is_owner = False
    vendor_profile = getattr(request.user, 'vendor_profile', None)
    if vendor_profile and invoice.vendor == vendor_profile:
        is_owner = True

    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to edit this invoice.")
        return redirect('profile')
    
    form_kwargs = {'instance': invoice, 'user': request.user}

    if request.method == "POST":
        form = VendorInvoiceForm(request.POST, **form_kwargs)
        if form.is_valid():
            form.save()
            messages.success(request, f"Vendor Invoice AP-{invoice.invoice_number} updated successfully.")
            return redirect("profile")
    else:
        form = VendorInvoiceForm(**form_kwargs)
        
    context = {'form': form, 'page_title': f'Edit Vendor Invoice AP-{invoice.invoice_number}'}
    return render(request, "Finance/vendor_invoice_form.html", context)
    
# ==================================
# === DELETE VIEWS ====
# ==================================

@login_required
def delete_customer_invoice(request, pk):
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    is_owner = False
    customer_profile = getattr(request.user, 'customer_profile', None)
    if customer_profile and invoice.customer == customer_profile:
        is_owner = True
        
    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to delete this invoice.")
        return redirect("profile")
    
    if request.method == "POST":
        invoice.delete()
        messages.success(request, f"Customer Invoice AR-{invoice.invoice_number} successfully deleted.")
        return redirect("profile") 
        
    context = {'invoice': invoice, 'page_title': f'Confirm Delete AR-{invoice.invoice_number}', 'invoice_type': 'customer'}
    return render(request, "Finance/confirm_delete_invoice.html", context)


@login_required
def delete_vendor_invoice(request, pk):
    invoice = get_object_or_404(VendorInvoice, pk=pk)
    
    is_owner = False
    vendor_profile = getattr(request.user, 'vendor_profile', None)
    if vendor_profile and invoice.vendor == vendor_profile:
        is_owner = True

    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to delete this invoice.")
        return redirect("profile")
    
    if request.method == "POST":
        invoice.delete()
        messages.success(request, f"Vendor Invoice AP-{invoice.invoice_number} successfully deleted.")
        return redirect("profile")
        
    context = {'invoice': invoice, 'page_title': f'Confirm Delete AP-{invoice.invoice_number}', 'invoice_type': 'vendor'}
    return render(request, "Finance/confirm_delete_invoice.html", context)