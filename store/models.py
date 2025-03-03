from django.utils import timezone
from django.db import models
from django.urls import reverse

from categories.models import Category, Size
from shop.settings import AUTH_USER_MODEL

# Create your models here.
"""
Product
-name
-price
-quantity
-description
-image
-created_at
-updated_at

"""

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', default=1)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='products', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    # return f"{self.name} ({self.quantity})"
    def get_absolute_url(self):
        return reverse('product', kwargs={'slug':self.slug})
    
class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "size")  # Évite les doublons

    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.stock} en stock)"
    
# Article(Order)
"""
-utilisateur
-produit
-quantité
-prix
-commandé ou non
"""

class Order(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE) # on_delete=models.CASCADE: si l'utilisateur est supprimé, on supprime aussi ses commandes
    product =models.ForeignKey(Product, on_delete=models.CASCADE)
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, null=True, default=1) 
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
# Panier(Cart)
"""
-utilisateur
-articles
-commandé ou non
-date de la commande
"""

class Cart(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order)
   

    def __str__(self):
        return f"{self.user.username}'s cart"
    
    def get_total(self):
        total = 0
        for order in self.orders.all():
            if order.product.price > 0:
                total += order.product.price * order.quantity
        return round(total, 2)
    
    def delete(self, *args, **kwargs):
        for order in self.orders.all():
            order.ordered = True
            order.ordered_date = timezone.now() # UTC correspond à l'heure de Londres , -2 correspond à l'heure de Paris
            order.save()
        self.orders.clear() # on supprime les articles du panier
        super().delete(*args, **kwargs)
    
