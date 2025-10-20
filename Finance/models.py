from django.db import models

class Customer(models.Model):
    COMPANY_CHOICES = [
        ('USPS', 'USPS'),
        ('PITTSBURG', 'Pittsburg'),
        ('TRANSLATION', 'Translation'),
        ('INTERPRETING', 'Interpreting'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company_code = models.CharField(max_length=20, choices=COMPANY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.company_code})"


class Vendor(models.Model):
    COMPANY_CHOICES = [
        ('USPS', 'USPS'),
        ('PITTSBURG', 'Pittsburg'),
        ('TRANSLATION', 'Translation'),
        ('INTERPRETING', 'Interpreting'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company_code = models.CharField(max_length=20, choices=COMPANY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.company_code})"
    

class CustomerInvoice(models.Model):
    # Cuentas por Cobrar (AR) - De Plunet a Bill.com
    STATUS_CHOICES = [
        ('OUTSTANDING', 'Outstanding'), 
        ('PAID', 'Paid'),               
        ('OVERDUE', 'Overdue'),         
        ('IN_TRANSIT', 'In Transit'),  
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_issued = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OUTSTANDING')
    payment_date = models.DateField(null=True, blank=True) 
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AR {self.invoice_number} - {self.customer.name}"

class VendorInvoice(models.Model):
    # Cuentas por Pagar (AP) - Gestionadas en Bill.com
    STATUS_CHOICES = [
        ('OUTSTANDING', 'Outstanding'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('PROCESSED', 'Processed')
    ]

    invoice_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date_issued = models.DateField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OUTSTANDING')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AP {self.invoice_number} - {self.vendor.name}"