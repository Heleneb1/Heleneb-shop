"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from account.views import signup, logout_user, login_user
from store.views import index, product_detail, add_to_cart_view, cart, delete_cart
from shop import settings

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('payment/', include('payments.urls')),
    path('signup/', signup, name='signup'),
    path('login/', login_user, name='login'),
    path('cart/', cart, name='cart'),
    path('cart/delete', delete_cart, name='delete-cart'),
    path('logout/', logout_user, name='logout'),
    path('product/<str:slug>', product_detail, name='product'),
    path('product/<str:slug>/add-to-cart', add_to_cart_view, name='add-to-cart'),

    ] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

## En production, on ne doit pas servir les fichiers statiques avec Django
## Il est recommandé de les servir avec un serveur web comme Nginx ou Apache
## Pour plus d'informations, voir la documentation officielle de Django