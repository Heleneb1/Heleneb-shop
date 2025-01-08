from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from store.models import Cart, Order, Product


class Shopper(AbstractUser):
   pass
        

def add_to_cart(user, slug):
    """
    Ajoute un produit au panier d'un utilisateur.
    :param user: utilisateur authentifié
    :param slug: slug du produit à ajouter
    """
    with transaction.atomic():
        product = get_object_or_404(Product, slug=slug)  # Le produit si existant
        if product.quantity <= 0:
            raise ValidationError(f"Stock insuffisant pour {product.name} (disponible : {product.quantity})")
        
        cart, _ = Cart.objects.get_or_create(user=user)  # Récupère ou crée le panier
        order, created = Order.objects.get_or_create(product=product,
                                                     user=user,
                                                     ordered=False)  # Commande existante ou nouvelle
        if created:
            cart.orders.add(order)  # Ajoute au panier si c'est une nouvelle commande
        else:
            order.quantity += 1  # Incrémente la quantité si déjà existante
            order.save()
        
        product.quantity -= 1  # Décrémente la quantité si déjà existante
        product.save()
        cart.save()