from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from account.views import signup, logout_user, login_user
from store.views import home, index, product_detail, add_to_cart_view, cart, delete_cart, remove_all_from_cart_view, remove_from_cart_view, search

from shop import settings

urlpatterns = [
    path('', home, name='home'),
    path('index/', index, name='index'),
    path('admin/', admin.site.urls),
    path('payment/', include('payments.urls')),
    path('categories/', include('categories.urls')),
    path('search/', search, name='search'),
    path('signup/', signup, name='signup'),
    path('login/', login_user, name='login'),
    path('cart/', cart, name='cart'),
    path('cart/delete', delete_cart, name='delete-cart'),
    path('logout/', logout_user, name='logout'),
    path('product/<str:slug>', product_detail, name='product'),
    path('product/<str:slug>/add-to-cart', add_to_cart_view, name='add-to-cart'),
    path('product/<str:slug>/remove-from-cart', remove_from_cart_view, name='remove-from-cart'),
    path('product/<slug:slug>/remove-all-from-cart/', remove_all_from_cart_view, name='remove-all-from-cart'),
    
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

## En production, on ne doit pas servir les fichiers statiques avec Django
## Il est recommandé de les servir avec un serveur web comme Nginx ou Apache
## Pour plus d'informations, voir la documentation officielle de Django
