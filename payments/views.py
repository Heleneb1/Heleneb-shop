from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.urls import reverse
import stripe
from django.conf import settings
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from shop.settings import AUTH_USER_MODEL
from .forms import AddressForm
from .models import Address

from store.models import Cart

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Associer l'adresse à l'utilisateur
            address.is_default = not Address.objects.filter(user=request.user, address_type=form.cleaned_data['address_type']).exists()  # Si aucune adresse de ce type, c'est la défaut
            address.save()
            return redirect('address_list')  # Rediriger vers la liste des adresses
    else:
        form = AddressForm()

    return render(request, 'add_address.html', {'form': form})

@login_required
def address_list(request):
    billing_addresses = Address.objects.filter(user=request.user, address_type='billing')
    shipping_addresses = Address.objects.filter(user=request.user, address_type='shipping')
    return render(request, 'address_list.html', {
        'billing_addresses': billing_addresses,
        'shipping_addresses': shipping_addresses
    })

# Vue pour afficher la page de paiement
# class CheckoutPageView(TemplateView):
#     template_name = 'payments/checkout.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
#         context['cart'] = Cart.objects.get(user=self.request.user)
#         return context

class CheckoutPageView(TemplateView):
    template_name = 'payments/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les adresses de facturation et de livraison
        billing_address = Address.objects.filter(user=self.request.user, address_type='billing', is_default=True).first()
        shipping_address = Address.objects.filter(user=self.request.user, address_type='shipping', is_default=True).first()

        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['cart'] = Cart.objects.get(user=self.request.user)
        context['billing_address'] = billing_address
        context['shipping_address'] = shipping_address
        
        return context

# Définir la clé secrète de Stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        print(cart.orders.all())  # Debug : vérifie si les articles sont bien là
        # Récupérer les adresses de facturation et de livraison
        # billing_address = Address.objects.filter(user=AUTH_USER_MODEL, address_type='billing', is_default=True).first()
        # shipping_address = Address.objects.filter(user=AUTH_USER_MODEL, address_type='shipping', is_default=True).first()


        line_items = []
        for order in cart.orders.all():
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': order.product.name,
                        'description': order.product.description[:100],
                    },
                    'unit_amount': int(order.product.price * 100),
                },
                'quantity': order.quantity,
            })

        # Créer la session uniquement si des articles existent
        if not line_items:
            return JsonResponse({'error': 'Le panier est vide.'}, status=400)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri('/payment/success/'),
                cancel_url=request.build_absolute_uri('/payment/cancel/'),
            )
            return JsonResponse({'sessionId': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# @method_decorator(csrf_exempt, name='dispatch')
# class CreateCheckoutSessionView(View):
#     def post(self, request, *args, **kwargs):
#         cart = get_object_or_404(Cart, user=request.user)
        
#         # Récupérer les adresses de facturation et de livraison
#         billing_address = Address.objects.filter(user=request.user, address_type='billing', is_default=True).first()
#         shipping_address = Address.objects.filter(user=request.user, address_type='shipping', is_default=True).first()

#         # Vérifier si les adresses existent
#         if not billing_address or not shipping_address:
#             return JsonResponse({'error': 'L\'adresse de facturation ou de livraison est manquante.'}, status=400)

#         # Créer les articles du panier
#         line_items = []
#         for order in cart.orders.all():
#             line_items.append({
#                 'price_data': {
#                     'currency': 'eur',
#                     'product_data': {
#                         'name': order.product.name,
#                         'description': order.product.description[:100],
#                     },
#                     'unit_amount': int(order.product.price * 100),
#                 },
#                 'quantity': order.quantity,
#             })

#         # Créer la session uniquement si des articles existent
#         if not line_items:
#             return JsonResponse({'error': 'Le panier est vide.'}, status=400)

#         try:
#             # Créer la session Stripe avec les adresses de facturation et de livraison
#             checkout_session = stripe.checkout.Session.create(
#                 payment_method_types=['card'],
#                 line_items=line_items,
#                 mode='payment',
#                 success_url=request.build_absolute_uri('/payment/success/'),
#                 cancel_url=request.build_absolute_uri('/payment/cancel/'),
#                 customer_email=request.user.email,  # Email du client
#                 shipping_address_collection={
#                     'allowed_countries': ['FR', 'US'],  # Liste des pays autorisés
#                 },
#                 billing_address_collection='auto',  # Stripe collectera automatiquement l'adresse de facturation
#                 shipping={
#                     'name': request.user.get_full_name(),
#                     'address': {
#                         'line1': shipping_address.address_line_1,
#                         'line2': shipping_address.address_line_2,
#                         'city': shipping_address.city,
#                         'postal_code': shipping_address.postal_code,
#                         'country': shipping_address.country,
#                     },
#                 },
#                 billing={
#                     'name': request.user.get_full_name(),
#                     'address': {
#                         'line1': billing_address.address_line_1,
#                         'line2': billing_address.address_line_2,
#                         'city': billing_address.city,
#                         'postal_code': billing_address.postal_code,
#                         'country': billing_address.country,
#                     },
#                 },
#             )
#             return JsonResponse({'sessionId': checkout_session.id})
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        cart.delete()  # Utilise votre logique de suppression existante
        return render(request, 'payments/success.html')

# Vues pour les pages de succès et d'échec
# class PaymentSuccessView(TemplateView):
#     template_name = 'payments/success.html'

class PaymentCancelView(TemplateView):
    template_name = 'payments/cancel.html'