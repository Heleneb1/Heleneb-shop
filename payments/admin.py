from django.contrib import admin

from payments.models import Address, Coupon, Payment

# Register your models here.
admin.site.register(Address)
admin.site.register(Coupon)
admin.site.register(Payment)
