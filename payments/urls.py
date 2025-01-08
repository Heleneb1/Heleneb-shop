from django.urls import path
from .views import (
    CheckoutPageView,
    CreateCheckoutSessionView,
    PaymentSuccessView,
    PaymentCancelView,
)

urlpatterns = [
    path('checkout/', CheckoutPageView.as_view(), name='checkout'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
]
