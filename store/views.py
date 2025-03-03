from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from account.models import add_to_cart, remove_from_cart
from django.core.paginator import Paginator
from categories.models import Category
from store.models import Cart, Product
from django.db.models import Q

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


def index(request):
   
    products = Product.objects.prefetch_related('sizes__size').filter(quantity__gt=0)  

    categories = Category.objects.all()
    for category in categories:
        if  not category.image:
            continue
        paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj,'products': products, 'categories': categories}

    return render(request, 'store/index.html', context= context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product_sizes = product.sizes.all()
    return render(request, 'store/detail.html', context={'product': product, 'product_sizes': product_sizes})

def add_to_cart_view(request, slug):
    if not request.user.is_authenticated:
        return redirect("login")
    
    size_name = request.POST.get("size")  # Récupération de la taille sélectionnée
    if not size_name:
        messages.error(request, "Veuillez sélectionner une taille.")
        return redirect('product', slug=slug)

    try:
        add_to_cart(request.user, slug, size_name)
        messages.success(request, "Produit ajouté au panier avec succès !")
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('cart')
def remove_from_cart_view(request, slug):
    """
    Vue pour supprimer un produit du panier.
    """
    if not request.user.is_authenticated:
        return redirect("login")  # Redirige si l'utilisateur n'est pas connecté

    remove_from_cart(request.user, slug)  # Appel de la fonction pour retirer du panier
    return redirect(reverse("cart"))  # Redirection vers la page du panier
def remove_all_from_cart_view(request, slug):
    """
    Vue pour supprimer un produit du panier.
    """
    if not request.user.is_authenticated:
        return redirect("login")  # Redirige si l'utilisateur n'est pas connecté

    remove_from_cart(request.user, slug)  # Appel de la fonction pour retirer du panier
    return redirect(reverse("cart"))  # Redirection vers la page du panier

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    
    orders = cart.orders.all() if cart else []
    total_quantity = sum(order.quantity for order in orders)
    return render(request, 'store/cart.html', context={'orders': orders, 'total_quantity': total_quantity, "cart": cart})

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

def search(request):
    query = request.GET.get('q', '')
    print("Requête de recherche :", query)  # Debugging

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        ).order_by('-created_at')
    else:
        products = Product.objects.none()  # Renvoie un queryset vide si pas de requête
    paginator = Paginator(products, 2)  # Affiche 4 résultats par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'products': products,'page_obj': page_obj, 'query': query}
    return render(request, 'store/search_result.html', context)


    # return render(request, 'store/index.html', {'products': products, 'query': query})


from django.http import HttpResponse

# def test_session(request):
#     request.session['test'] = 'Django session active'
#     return HttpResponse(f"Session test: {request.session.get('test', 'Session non trouvée')}")
