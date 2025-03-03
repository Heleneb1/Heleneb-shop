from django.db import models
from django.conf import settings
from store.models import Order


class Address(models.Model):
    ADDRESS_TYPES = (
        ('billing', 'Billing Address'),
        ('shipping', 'Shipping Address'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default='John')
    last_name = models.CharField(max_length=50, default='Doe')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    is_default = models.BooleanField(default=False)  # Pour savoir si c'est l'adresse par défaut

    def save(self, *args, **kwargs):
        # Si cette adresse est définie comme par défaut, désactiver les autres du même type
        if self.is_default:
            Address.objects.filter(user=self.user, address_type=self.address_type).update(is_default=False)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.address_type} - {"Default" if self.is_default else "Not Default"}'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username if self.user else "Anonymous Payment"


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"Refund {self.pk}"


class LineOrder(models.Model):
    quantity = models.IntegerField()
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    shipping_details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} - {self.quantity} units"
