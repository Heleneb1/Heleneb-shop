## Ajout des templates html

créer le template directory à la racine du projet

dans les nouvelles versions de Django pas besoin de faire l'import de os simplement:

```python
 DIRS': [BASE_DIR / "templates"],
```

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

```

4. clone repoBACK

```
git clone https://github.com/WildCodeSchool/bugs-squad-project-backend.git
```

## Ajouter la Gestion d'image

### 1. Affichage des images dans les templates

Pour afficher une image associée à un produit dans un template Django, utilisez le code suivant :

```html
<img src="{{ product.thumbnail.url }}" />
```

Remarque : thumbnail est un champ de type ImageField dans ton modèle, et .url permet de récupérer l'URL de l'image.

Voir la doc de django

dans l'urls du site, ou se trouve le fichier settings apres la liste on ajoute

```python
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

on ajoute cet import:

```python
from django.conf.urls.static import static
```

ainsi que

```python
from shop import settings
```

Actuellement le modele est ainsi :

```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='products', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

tous les thumbnails sont uploader dans le dossier products, mais on peut changer cela en ajoutant un sous dossier pour chaque produit

On va devoir deplacer le sous dossier products dans le dossier media et faire de meme pour les images
afin de pouvoir les afficher dans les templates

enfin on ajoute dans les settings

```python
MEDIA_URL ="/media/"
MEDIA_ROOT = BASE_DIR/"media"
```

**MEDIA_URL** contient le chemin relatif pour accéder aux fichiers médias, et **MEDIA_ROOT** contient le chemin absolu vers le dossier où les fichiers médias sont stockés.

Documentation Django
Pour plus d'informations, consulte [la documentation officielle](https://docs.djangoproject.com/en/5.1/topics/files/) sur les fichiers statiques et médias.

## Ajout d'un champs Slug

Pour ajouter un champ slug à un modèle, il faut ajouter un champ de type SlugField à ton modèle. Ce champ est utilisé pour générer des URL lisibles par les humains.

```python
slug = models.SlugField(max_length=255, unique=True)
```

Ajouter l'url dans le fichier urls.py

```python
path('products/<str:slug>', product_detail, name='product'),
```

## Ajout de la page de détail d'un produit

Pour ajouter une page de détail d'un produit, il faut créer une vue qui prend en paramètre le slug du produit et qui renvoie le template de la page de détail du produit.

```python
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={'product': product})
```

## Accès à la page de détail d'un produit

2 solutions pour accéder à la page de détail d'un produit :

1. Ajouter un lien vers la page de détail du produit dans la liste des produits

2. Rediriger l'utilisateur vers la page de détail du produit lorsqu'il clique sur un produit
   creer une methode dans le modele Product
   on aussi y acceder via l'interface admin pour voir le produit

```python
    def get_absolute_url(self):
        return reverse('product', kwargs={'slug':self.slug})
```

l'ajouter dans le template

```html
<a href="{{ product.get_absolute_url }}">{{ product.name }}</a>
```

ou dans le template

```html
<a href="{% url 'product' slug=product.slug %}">{{ product.name }}</a>
```

# Creer une nouvelle app

```bash
python manage.py startapp store
```

```bash
python manage.py startapp account
```

Puis l'ajouter dans les settings

# Créer un json pour recuperer les données déjà enregistrées

```bash
python manage.py dumpdata store.Product > store_products.json
```

ici les données sont stockées dans le fichier store_products.json et ce sont les données de la table Product
store est le nom de l'app
pour importer les données

```bash
python manage.py loaddata store_products.json
```

faire un json de la table user

```bash
python manage.py dumpdata account.Shopper > account_shoppers.json
```

### Dans le cas suivant

python manage.py makemigrations
It is impossible to add a non-nullable field 'user' to cart without specifying a default. This is because the database needs something to populate existing rows.
Please select a fix:

1.  Provide a one-off default now (will be set on all existing rows with a null value for this column)
2.  Quit and manually define a default value in models.py.

le champ user ne peut pas etre null, il faut lui donner une valeur par defaut

on peut selectionner l'option 1 et donner une valeur par defaut

ici on a donné une chaine vide

```python
""
```
# helenebshop
