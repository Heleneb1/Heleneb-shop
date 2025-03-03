from django.shortcuts import get_object_or_404, render
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
from payments.models import Address
from store.models import Cart

# Définir la clé secrète de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address_type = request.POST.get('address_type', 'billing')  # Récupérer le type d'adresse
            
            # Gérer l'adresse par défaut
            if address_type == 'billing':
                if 'set_default_billing' in request.POST:
                    address.is_default = True
                else:
                    Address.objects.filter(user=request.user, address_type='billing').update(is_default=False)
            
            elif address_type == 'shipping':
                if 'set_default_shipping' in request.POST:
                    address.is_default = True
                else:
                    Address.objects.filter(user=request.user, address_type='shipping').update(is_default=False)

            address.address_type = address_type
            address.save()
            return redirect('checkout')  # Rediriger après enregistrement
        else:
            print(form.errors)  # Debug
            return render(request, 'payments/checkout.html', {'form': form, 'error': 'Erreur lors de l\'ajout de l\'adresse.'})

    else:
        form = AddressForm()

    return render(request, 'payments/checkout.html', {'form': form})

@login_required
def address_list(request):
    billing_addresses = Address.objects.filter(user=request.user, address_type='billing')
    shipping_addresses = Address.objects.filter(user=request.user, address_type='shipping')
    return render(request, 'address_list.html', {
        'billing_addresses': billing_addresses,
        'shipping_addresses': shipping_addresses
    })

class CheckoutPageView(TemplateView):
    template_name = 'payments/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Vérifier si l'utilisateur a déjà des adresses valides
        billing_address = Address.objects.filter(
            user=self.request.user, 
            address_type='billing', 
            is_default=True
        ).first()
        
        shipping_address = Address.objects.filter(
            user=self.request.user, 
            address_type='shipping', 
            is_default=True
        ).first()

        # Créer UNIQUEMENT si aucune adresse de ce type n'existe
        if not shipping_address:
            first_shipping = Address.objects.filter(user=self.request.user, address_type='shipping').first()
            if first_shipping:
                first_shipping.is_default = True
                first_shipping.save()
                shipping_address = first_shipping

        if not billing_address:
            first_billing = Address.objects.filter(user=self.request.user, address_type='billing').first()
            if first_billing:
                first_billing.is_default = True
                first_billing.save()
                billing_address = first_billing


        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['cart'] = Cart.objects.get(user=self.request.user)
        context['billing_address'] = billing_address
        context['shipping_address'] = shipping_address

        return context
# @method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        shipping_address = Address.objects.filter(user=request.user, address_type='shipping', is_default=True).first()
        billing_address = Address.objects.filter(user=request.user, address_type='billing', is_default=True).first()
        print(cart.orders.all())  # Debug : vérifie si les articles sont bien là

        line_items = []
        for order in cart.orders.all():
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': order.product.name,
                        # 'description': order.product.description[:100],
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
                billing_address_collection='required',
                shipping_address_collection={'allowed_countries': ['FR']},
                
                success_url=request.build_absolute_uri('/payment/success/'),
                cancel_url=request.build_absolute_uri('/payment/cancel/'),
            )
            print("Billing Address:", billing_address)
            print("Shipping Address:", shipping_address)

            return JsonResponse({'sessionId': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        # Récupérer et vider le panier après paiement réussi
        cart = Cart.objects.get(user=request.user)
        cart.delete()
        return render(request, 'payments/success.html')

class PaymentCancelView(TemplateView):
    template_name = 'payments/cancel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Permettre à l'utilisateur de retrouver son panier en cas d'annulation
        context['cart'] = Cart.objects.get(user=self.request.user)
        return context