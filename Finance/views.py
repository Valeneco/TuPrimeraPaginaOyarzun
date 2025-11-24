from datetime import date 
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404

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

# === INVOICE MANAGEMENT (CREATE) ===
@login_required
def add_customer_invoice(request):
    # === 1. VERIFICACIÓN DE SEGURIDAD (Solo Clientes) ===
    if not hasattr(request.user, 'customer_profile') or request.user.user_type != 'C':
        messages.error(request, "You are not authorized to create this type of invoice.")
        return redirect('profile') 
        
    if request.method == "POST":
        form = CustomerInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            
            # 2. Asignar Customer (Requerido)
            try:
                invoice.customer = request.user.customer_profile
            except AttributeError:
                 messages.error(request, "Error: Customer profile link missing.")
                 return redirect('profile')

            # 3. Asignar Date Issued (Requerido)
            invoice.date_issued = date.today()
            
            # 4. Asignar Status (Requerido)
            invoice.status = 'OUTSTANDING'
            
            # 5. Guarda en la base de datos
            invoice.save()
            
            # 6. Mensaje y Redirección 
            messages.success(request, "Customer invoice created successfully!")
            return redirect("profile")
            
        else:
            # === DEPURACIÓN: IMPRIME ERRORES DE FORMULARIO EN LA CONSOLA ===
            print("=========================================")
            print("FORMULARIO INVÁLIDO. ERRORES DETECTADOS:")
            print(form.errors) 
            print("=========================================")
            messages.error(request, "Error: Please correct the marked fields.")
            
    else:
        form = CustomerInvoiceForm()
        
    return render(request, "Finance/customer_invoice_form.html", {'form': form, 'page_title': 'Add Customer Invoice (AR)'})

@login_required
def add_vendor_invoice(request):
    # Es buena práctica verificar si es Vendor o Staff antes de crear
    if not (hasattr(request.user, 'vendor_profile') and request.user.user_type == 'V') and not request.user.is_staff:
        messages.error(request, "You are not authorized to create this type of invoice.")
        return redirect('profile') 
        
    if request.method == "POST":
        form = VendorInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            
            # Si es un Vendor, asignarlo automáticamente
            if request.user.user_type == 'V':
                invoice.vendor = request.user.vendor_profile
            
            invoice.date_issued = date.today()
            invoice.status = 'OUTSTANDING'
            
            invoice.save()
            messages.success(request, "Vendor invoice created successfully!")
            return redirect("profile")
    else:
        form = VendorInvoiceForm()
        
    return render(request, "Finance/vendor_invoice_form.html", {'form': form, 'page_title': 'Add Vendor Invoice (AP)'})

# === INVOICE MANAGEMENT (READ LIST & DETAIL) ===
@login_required
def invoice_list(request):
    invoices = CustomerInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    return render(request, "Finance/invoice_list.html", {'invoices': invoices, 'page_title': 'Outstanding AR Invoices'})

@login_required
def vendor_payment_list(request):
    invoices = VendorInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    return render(request, "Finance/vendor_invoice_list.html", {'invoices': invoices, 'page_title': 'Pending AP Payments'})


@login_required
def invoice_detail(request, pk):
    """Muestra el detalle de una CustomerInvoice o VendorInvoice y da opciones CRUD al staff o al dueño."""
    
    invoice = None
    invoice_type = None
    related_user_profile = None 

    # 1. Intenta obtener como CustomerInvoice (AR)
    try:
        invoice = CustomerInvoice.objects.get(pk=pk)
        invoice_type = 'customer'
        related_user_profile = invoice.customer 
    except CustomerInvoice.DoesNotExist:
        # 2. Si no es AR, intenta obtener como VendorInvoice (AP)
        try:
            invoice = VendorInvoice.objects.get(pk=pk)
            invoice_type = 'vendor'
            related_user_profile = invoice.vendor
        except VendorInvoice.DoesNotExist:
            raise Http404("Invoice does not exist.") 

    # 3. VERIFICACIÓN DE SEGURIDAD (Permite Staff O Dueño)
    
    is_authorized = request.user.is_staff 
    is_owner = False # Bandera para saber si es el dueño
    
    # Solo intentamos verificar la propiedad si el perfil relacionado existe y tiene un usuario vinculado
    if related_user_profile and hasattr(related_user_profile, 'user') and related_user_profile.user == request.user:
        is_authorized = True
        is_owner = True # Es el dueño

    # Creamos la variable que usaremos en el template: puede editar si es Staff O dueño
    can_edit = is_authorized 
    
    # === DEBUG IMPRESIÓN ===
    print("--- DEBUG AUTHORIZATION ---")
    print(f"Logged in User: {request.user.username} (Staff: {request.user.is_staff})")
    
    owner_user = 'N/A (Profile exists but user field missing or null)'
    if related_user_profile and hasattr(related_user_profile, 'user'):
        owner_user = related_user_profile.user
        
    print(f"Invoice Owner User (from profile): {owner_user}")
    print(f"Is Authorized (Can View): {is_authorized}")
    print(f"Can Edit/Delete: {can_edit}")
    print("---------------------------")
    # ==========================================

    if not is_authorized:
        messages.error(request, "You are not authorized to view this invoice.")
        return redirect('profile')

    context = {
        'invoice': invoice,
        'invoice_type': invoice_type,
        'page_title': f"Invoice Detail: {invoice.invoice_number}",
        # *** CAMBIO CLAVE: Pasamos la variable can_edit a la plantilla ***
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
# ==================================
# === UPDATE (Actualizar) VIEWS (Corregidas para DUEÑO) ====
# ==================================

@login_required
def edit_customer_invoice(request, pk):
    """Permite editar una factura de Cliente (AR) si es Staff O el dueño."""
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    # --- VERIFICACIÓN DE PERMISOS ---
    # Verificar si el usuario es el dueño de la factura
    is_owner = hasattr(request.user, 'customer_profile') and invoice.customer.user == request.user
    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to edit this invoice.")
        return redirect('profile')
    # ---------------------------------
    
    # *** CAMBIO CLAVE: Pasamos el usuario al formulario ***
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
    """Permite editar una factura de Proveedor (AP) si es Staff O el dueño."""
    invoice = get_object_or_404(VendorInvoice, pk=pk)
    
    # --- VERIFICACIÓN DE PERMISOS ---
    # Verificar si el usuario es el dueño de la factura
    is_owner = hasattr(request.user, 'vendor_profile') and invoice.vendor.user == request.user
    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to edit this invoice.")
        return redirect('profile')
    # ---------------------------------
    
    # *** CAMBIO CLAVE: Pasamos el usuario al formulario ***
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
# === DELETE (Borrar) VIEWS (Corregidas para DUEÑO) ====
# ==================================

@login_required
def delete_customer_invoice(request, pk):
    """Permite eliminar una factura de Cliente (AR) si es Staff O el dueño."""
    invoice = get_object_or_404(CustomerInvoice, pk=pk)
    
    # --- VERIFICACIÓN DE PERMISOS ---
    # Verificar si el usuario es el dueño de la factura
    is_owner = hasattr(request.user, 'customer_profile') and invoice.customer.user == request.user
    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to delete this invoice.")
        return redirect("profile")
    # ---------------------------------
    
    if request.method == "POST":
        invoice.delete()
        messages.success(request, f"Customer Invoice AR-{invoice.invoice_number} successfully deleted.")
        return redirect("profile") 
        
    # Añadir 'invoice_type' al contexto para que la plantilla sepa qué nombre mostrar
    context = {'invoice': invoice, 'page_title': f'Confirm Delete AR-{invoice.invoice_number}', 'invoice_type': 'customer'}
    return render(request, "Finance/confirm_delete_invoice.html", context)


@login_required
def delete_vendor_invoice(request, pk):
    """Permite eliminar una factura de Proveedor (AP) si es Staff O el dueño."""
    invoice = get_object_or_404(VendorInvoice, pk=pk)
    
    # --- VERIFICACIÓN DE PERMISOS ---
    # Verificar si el usuario es el dueño de la factura
    is_owner = hasattr(request.user, 'vendor_profile') and invoice.vendor.user == request.user
    if not (request.user.is_staff or is_owner):
        messages.error(request, "You are not authorized to delete this invoice.")
        return redirect("profile")
    # ---------------------------------
    
    if request.method == "POST":
        invoice.delete()
        messages.success(request, f"Vendor Invoice AP-{invoice.invoice_number} successfully deleted.")
        return redirect("profile")
        
    # Añadir 'invoice_type' al contexto para que la plantilla sepa qué nombre mostrar
    context = {'invoice': invoice, 'page_title': f'Confirm Delete AP-{invoice.invoice_number}', 'invoice_type': 'vendor'}
    return render(request, "Finance/confirm_delete_invoice.html", context)