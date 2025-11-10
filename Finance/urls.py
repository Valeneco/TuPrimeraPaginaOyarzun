from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),

    # === REDIRECTED FORM VIEWS ===
    path('add_customer/', views.add_customer, name='add_customer'),
    path('add_vendor/', views.add_vendor, name='add_vendor'),

    # === INVOICE MANAGEMENT ===
    path('add_customer_invoice/', views.add_customer_invoice, name='add_customer_invoice'),
    path('add_vendor_invoice/', views.add_vendor_invoice, name='add_vendor_invoice'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('vendors/', views.vendor_payment_list, name='vendor_payment_list'),

    # === SEARCH VIEWS ===
    path('search_customers/', views.search_customers, name='search_customers'),
    path('search_vendors/', views.search_vendors, name='search_vendors'),

    # === ADMIN HOME PENDING LISTS ===
    path('pending_ar/', views.pending_ar_list, name='pending_ar_list'),
    path('pending_ap/', views.pending_ap_list, name='pending_ap_list'),
]
