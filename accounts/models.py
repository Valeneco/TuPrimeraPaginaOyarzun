from django.contrib.auth.models import AbstractUser
from django.db import models
from Finance.models import Customer, Vendor

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)

    USER_TYPE_CHOICES = (
        ('C', 'Customer'),
        ('V', 'Vendor'),
    )
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES, default='C')
    customer_profile = models.OneToOneField(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    vendor_profile = models.OneToOneField(Vendor, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
