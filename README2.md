# Creer un systeme de paiement avec Stripe

## Introduction

Stripe est une plateforme de paiement en ligne qui permet de gerer les transactions financieres de maniere securisee. Elle est tres utilisee par les entreprises pour gerer les paiements de leurs clients. Dans ce tutoriel, nous allons voir comment creer un systeme de paiement avec Stripe en utilisant le langage de programmation Python.

## Installation

.1. Creer un compte sur le site de Stripe
.2. Installer la bibliotheque Stripe en utilisant la commande suivante:

```bash
pip install stripe
```

et

```bash
pip install django-stripe-payments
```

.3. Configurer votre compte Stripe en recuperant votre cle d'API publique et privee en mode test.

## Implementation

.1. Creer un fichier de configuration pour stocker vos cles d'API:

```python
# config.py
STRIPE_PUBLIC_KEY = 'votre_cle_publique'
STRIPE_SECRET = 'votre_cle_secrete'
```

.2. Creer une vue pour gerer le paiement:

```python
python manage.py startapp payments
```

dans INSTALLED_APPS ajouter

```python
 "payments",
```

### Ajouter la logique de paiement dans le fichier views.py

```python

from django.shortcuts import render
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET

def payment(request):
    return render(request, 'payments/payment.html')


```

### Annulation repo git

```bash
rm -rf .git

```

Cela supprimera l'historique Git local tout en gardant les fichiers du projet, annule le git init et vous permet de recommencer l'initialisation de Git.
