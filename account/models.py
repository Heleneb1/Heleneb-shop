from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from store.models import Cart, Order, Product


class Shopper(AbstractUser):
   pass
        

def add_to_cart(user, slug, size_name):
    """
    Ajoute un produit au panier d'un utilisateur en fonction de la taille choisie.
    :param user: utilisateur authentifié
    :param slug: slug du produit à ajouter
    :param size_name: taille choisie pour le produit
    """
    with transaction.atomic():
        # Récupère le produit en fonction du slug
        product = get_object_or_404(Product, slug=slug)
        
        # Récupère la taille sélectionnée par l'utilisateur
        product_size = product.sizes.filter(size__name=size_name).first()
        
        if not product_size:
            raise ValidationError(f"La taille {size_name} n'est pas disponible pour {product.name}")

        # Vérification du stock du produit et de la taille avant toute modification
        if product.quantity <= 0:
            raise ValidationError(f"Stock insuffisant pour {product.name} (disponible : {product.quantity})")
        
        if product_size.stock <= 0:
            raise ValidationError(f"Stock insuffisant pour {product.name} en taille {size_name} (disponible : {product_size.stock})")

        # Récupère ou crée le panier de l'utilisateur
        cart, _ = Cart.objects.get_or_create(user=user)

        # Récupère ou crée la commande pour ce produit et cette taille
        order, created = Order.objects.get_or_create(
            product=product,
            user=user,
            product_size=product_size,
            ordered=False
        )

        if created:
            cart.orders.add(order)  # Ajoute la commande au panier si elle est nouvelle
        else:
            order.quantity += 1  # Incrémente la quantité si la commande existe déjà
            order.save()

        # Mise à jour des stocks
        product.quantity -= 1
        product_size.stock -= 1

        # Sauvegarde les modifications dans la base de données
        product.save()
        product_size.save()
        cart.save()  
        
def remove_from_cart(user, slug):
    """
    Retire un produit du panier de l'utilisateur.
    """
    with transaction.atomic():
        product = get_object_or_404(Product, slug=slug)
        cart = Cart.objects.filter(user=user).first()  
        if not cart:
            return  # Pas de panier, rien à retirer

        order = Order.objects.filter(product=product, user=user, ordered=False).first()
        if not order:
            return  # Pas de commande en attente pour ce produit

        if order.quantity > 1:
            order.quantity -= 1
            order.save()
        else:
            cart.orders.remove(order)
            order.delete()

        # On augmente le stock après le retrait
        product.quantity += 1
        product.save()
        cart.save()

def remove_all_from_cart(user, slug):
    """
    Retire un produit du panier de l'utilisateur et met à jour le stock.
    """
    try:
        with transaction.atomic():
            # Récupération du produit
            product = get_object_or_404(Product, slug=slug)
            # Récupération du panier de l'utilisateur
            cart = Cart.objects.filter(user=user).first()
            
            if not cart:
                return "Pas de panier trouvé pour cet utilisateur."
            
            # Récupération de la commande en attente pour ce produit
            order = Order.objects.filter(product=product, user=user, ordered=False).first()
            
            if not order:
                return "Aucune commande en attente pour ce produit."
            
            # Mise à jour du stock après retrait
            product.quantity += order.quantity
            product.save()
            
            # Retrait de la commande du panier
            cart.orders.remove(order)
            order.delete()
            
            cart.save()
            return "Produit retiré avec succès du panier."

    except Exception as e:
        return f"Erreur lors de la suppression : {str(e)}"