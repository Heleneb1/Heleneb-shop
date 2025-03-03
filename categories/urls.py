from django.urls import path

from categories.views import category_list, product_by_category


urlpatterns = [
    path('categories', category_list, name='category_list'),
    path('<slug:slug>/', product_by_category, name='products_by_category'),
]
