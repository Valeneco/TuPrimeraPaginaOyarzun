from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomerForm, CustomerInvoiceForm, VendorInvoiceForm , VendorForm
from .models import Customer, CustomerInvoice, Vendor, VendorInvoice
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import date
from dateutil.relativedelta import relativedelta


# VISTAS BASE
def index(request):
    return render(request,"Finance/index.html")

def test(request):
    return render(request, "Finance/test.html")

def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("invoice_list") 
    else:
        form = CustomerForm()
    return render(request, "Finance/customer_form.html", {'form': form}) 

def add_customer_invoice(request):
    if request.method == "POST":
        form = CustomerInvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("invoice_list") 
    else:
        form = CustomerInvoiceForm()
    return render(request, "Finance/customer_invoice_form.html", {'form': form, 'page_title': 'Añadir Factura de Cliente (AR)'})

def add_vendor_invoice(request):
    if request.method == "POST":
        form = VendorInvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("vendor_payment_list") 
    else:
        form = VendorInvoiceForm()
    return render(request, "Finance/vendor_invoice_form.html", {'form': form, 'page_title': 'Añadir Factura de Proveedor (AP)'})


def invoice_list(request):
    """Vista AR: Muestra facturas 'Outstanding' listas para sincronizar."""
   
    invoices = CustomerInvoice.objects.filter(status='OUTSTANDING').order_by('-date_issued')
    
    context = {
        'invoices': invoices,
        'page_title': 'Facturas AR Outstanding (Origen Plunet)'
    }
    return render(request, "Finance/invoice_list.html", context)


def vendor_payment_list(request):
    """Vista AP: Muestra pagos a proveedores (control Bill.com)."""
    vendors = Vendor.objects.all().prefetch_related('vendorinvoice_set').order_by('name')
    
    context = {
        'vendors': vendors,
        'page_title': 'Pagos AP a Proveedores (Gestionado en Bill.com)'
    }
    return render(request, "Finance/vendor_list.html", context)


def search_customers(request):
    """Permite buscar clientes por nombre o código."""
    query = request.GET.get('q')
    customers = None
    
    if query:
        # Búsqueda insensible a mayúsculas/minúsculas en Nombre y Código
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(company_code__icontains=query)
        ).order_by('name')

    context = {
        'customers': customers,
        'query': query,
        'page_title': 'Buscar Clientes'
    }
    return render(request, "Finance/search_customer.html", context)

def add_vendor(request):
    """Permite añadir un nuevo proveedor."""
    if request.method == "POST":
        form = VendorForm(request.POST) 
        if form.is_valid():
            form.save()
            return redirect('index') 
    else:
        form = VendorForm()
    # Finance/views.py

from django.shortcuts import render, redirect # << Asegúrate de importar 'redirect'
from .forms import VendorForm 
# ... (otras importaciones)

def add_vendor(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            # Si pasa aquí, se guarda y redirige.
            form.save()
            print("--- VENDOR GUARDADO CORRECTAMENTE ---") 
            return redirect('index') 
        else:
            # Si falla, imprime los errores en la terminal.
            print("--- ERROR: FORMULARIO NO VÁLIDO ---")
            print(form.errors) # <-- ESTA LÍNEA MUESTRA LA CAUSA DEL FALLO
            # La ejecución continúa, renderizando la plantilla con el formulario fallido
            
    else:
        # Método GET: Muestra el formulario vacío
        form = VendorForm() 
    
    context = {'form': form}
    return render(request, 'Finance/vendor_form.html', context)


def search_vendors(request):
    """Permite buscar proveedores por nombre o código."""
    query = request.GET.get('q')
    vendors = None
    
    if query:
        # Búsqueda insensible a mayúsculas/minúsculas en Nombre y Código
        vendors = Vendor.objects.filter(
            Q(name__icontains=query) | Q(company_code__icontains=query)
        ).order_by('name')

    context = {
        'vendors': vendors,
        'query': query,
        'page_title': 'Buscar Proveedores'
    }
    return render(request, "Finance/search_vendor.html", context)