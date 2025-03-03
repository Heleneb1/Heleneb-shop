from django.contrib import admin

from categories.models import Category, Size
from store.models import ProductSize



from .models import Shopper

# Register your models here.
admin.site.register(Shopper)

admin.site.register(Category)
admin.site.register(ProductSize)
admin.site.register(Size)