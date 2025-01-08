from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from account.models import add_to_cart
from store.models import Cart, Order, Product

# Create your views here.

def index(request):
    products=Product.objects.all()
    return render(request, 'store/index.html', context= {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={'product': product})

def add_to_cart_view(request, slug):
    """
    Vue pour ajouter un produit au panier
    """
    if not request.user.is_authenticated:
        return redirect("login")  # Redirige si l'utilisateur n'est pas connecté

    add_to_cart(request.user, slug)  # Appel de la fonction pour ajouter au panier
    return redirect(reverse("product", kwargs={'slug': slug}))  # Redirection après ajout

def cart(request) :
    cart = get_object_or_404(Cart, user= request.user)
    return render(request, 'store/cart.html', context={'orders': cart.orders.all()})

def delete_cart(request):
    # cart = request.user.cart
    # if cart:
    #     cart.orders.all().delete()
    #     cart.delete()
    # return redirect('index')
    # methode wallrus
    if cart := request.user.cart: # on verifie et on assigne la valeur de request.user.cart à cart
        # on utilse la meethode delete du model
        cart.delete()
    return redirect('index')